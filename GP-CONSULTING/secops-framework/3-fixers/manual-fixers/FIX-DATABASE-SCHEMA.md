# Manual Fix Guide: Database Schema (CVV/PIN Removal)

## Problem

**PCI-DSS Violation:** Storage of CVV/PIN violates card data security requirements
- **Requirement:** PCI-DSS 3.2.2 - Do not store CVV2/CVC2/CID
- **Requirement:** PCI-DSS 3.2.3 - Do not store PIN/PIN block
- **Risk:** CRITICAL - Immediate PCI-DSS non-compliance
- **Current State:** `payments` table contains `cvv`, `pin`, and full `card_number` columns

## Solution

Remove prohibited fields and implement tokenization using external PCI-compliant vault.

## Prerequisites

- Database backup completed
- PCI-compliant tokenization service (Stripe, Adyen, or Basis Theory)
- Maintenance window scheduled
- Migration tested in staging

## Step-by-Step Instructions

### Step 1: Choose Tokenization Provider

**Option A: Stripe (Recommended)**
```bash
npm install stripe

# Tokenize card
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const paymentMethod = await stripe.paymentMethods.create({
  type: 'card',
  card: {
    number: '4242424242424242',
    exp_month: 12,
    exp_year: 2025,
    cvc: '123',
  },
});

// Store only: paymentMethod.id (e.g., pm_1Abc123)
```

**Option B: Basis Theory (Tokenization-as-a-Service)**
```bash
npm install @basis-theory/basis-theory-js

const { BasisTheory } = require('@basis-theory/basis-theory-js');
const bt = await new BasisTheory().init(process.env.BT_API_KEY);

const token = await bt.tokens.create({
  type: 'card',
  data: {
    number: '4242424242424242',
    expiration_month: 12,
    expiration_year: 2025,
    cvc: '123'
  }
});

// Store only: token.id
```

### Step 2: Run Database Migration

See migration script in: `secops/3-fixers/auto-fixers/fix-database.sh`

```sql
-- This migration PERMANENTLY removes:
-- 1. card_number column
-- 2. cvv column
-- 3. pin column
--
-- And replaces with:
-- 1. token_id (references payment_tokens table)
-- 2. last_four (last 4 digits for display)
```

### Step 3: Update Backend Payment Flow

```javascript
// OLD (INSECURE):
const payment = await Payment.create({
  merchant_id: req.body.merchant_id,
  amount: req.body.amount,
  card_number: req.body.card_number,  // ❌ PCI-DSS violation
  cvv: req.body.cvv,                   // ❌ PROHIBITED
  pin: req.body.pin,                   // ❌ PROHIBITED
});

// NEW (PCI-DSS COMPLIANT):
const { tokenizeCard } = require('../services/tokenization.service');

const tokenData = await tokenizeCard(
  req.body.card_number,
  req.body.cvv,
  req.body.expiry_month,
  req.body.expiry_year
);

const payment = await Payment.create({
  merchant_id: req.body.merchant_id,
  amount: req.body.amount,
  token_id: tokenData.token_id,  // ✅ Only store token reference
});
```

### Step 4: Update Payment Processing

```javascript
// Process payment using token
async function processPayment(paymentId) {
  const payment = await Payment.findByPk(paymentId, {
    include: [{ model: PaymentToken }]
  });

  // Call Stripe with token (never store full card details)
  const charge = await stripe.charges.create({
    amount: payment.amount * 100,
    currency: 'usd',
    source: payment.PaymentToken.token_reference,  // Stripe payment method ID
  });

  return charge;
}
```

### Step 5: Verify PCI-DSS Compliance

```bash
# Verify no prohibited fields exist
psql securebank -c "\d payments"

# Expected: NO cvv, pin, or card_number columns

# Run Bandit scan
bandit -r backend/ | grep -i "cvv\|pin\|card_number"

# Expected: No results
```

## Migration Checklist

- [ ] Backup production database
- [ ] Test migration in staging environment
- [ ] Integrate tokenization provider (Stripe/Basis Theory)
- [ ] Update payment controller to use tokens
- [ ] Run migration script
- [ ] Verify no CVV/PIN data remains
- [ ] Update frontend to send to tokenization API directly
- [ ] Re-scan with Bandit/Semgrep
- [ ] Document token lifecycle

## Rollback Plan

**WARNING:** This migration is IRREVERSIBLE - CVV/PIN data will be permanently deleted.

To rollback schema changes only:

```sql
-- Restore from backup (does not restore deleted data)
psql securebank < backup-$(date +%Y%m%d).sql
```

## Compliance Impact

**Before:**
- ❌ PCI-DSS 3.2.2 - FAIL (CVV storage)
- ❌ PCI-DSS 3.2.3 - FAIL (PIN storage)
- ❌ PCI-DSS SAQ-D required (full audit)

**After:**
- ✅ PCI-DSS 3.2.2 - PASS (no CVV)
- ✅ PCI-DSS 3.2.3 - PASS (no PIN)
- ✅ PCI-DSS SAQ-A eligible (reduced scope)

**Cost Reduction:**
- Full PCI audit: $50K-150K/year → $5K-10K/year (SAQ-A)
- Tokenization cost: $0.05-0.10 per transaction

## References

- [PCI-DSS Requirement 3.2](https://www.pcisecuritystandards.org/)
- [Stripe Tokenization](https://stripe.com/docs/payments/payment-methods)
- [Basis Theory Vault](https://docs.basistheory.com/)

---

**Severity:** CRITICAL | **Effort:** 3 hours | **Downtime:** 30 minutes
