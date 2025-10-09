#!/bin/bash
set -e

echo "🔧 Auto-Fixer: Database Schema (CVV/PIN Removal)"
echo "═══════════════════════════════════════════════"

BACKEND_DIR="../../../../backend"
MODELS_DIR="$BACKEND_DIR/models"

echo ""
echo "⚠️  WARNING: This script will modify the database schema!"
echo "   - CVV and PIN columns will be removed"
echo "   - Payment tokenization will be implemented"
echo "   - This is a DESTRUCTIVE operation"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "❌ Aborted"
  exit 1
fi

echo ""
echo "→ Creating database migration..."

mkdir -p "$BACKEND_DIR/migrations"

cat > "$BACKEND_DIR/migrations/001_remove_pci_violations.sql" << 'EOF'
-- Migration: Remove PCI-DSS violations from Payment table
-- Author: SecOps Auto-Fixer
-- Date: 2025-10-08

BEGIN;

-- Step 1: Create tokenization table
CREATE TABLE IF NOT EXISTS payment_tokens (
  id SERIAL PRIMARY KEY,
  payment_id INTEGER NOT NULL REFERENCES payments(id),
  token_reference VARCHAR(255) NOT NULL UNIQUE,
  last_four VARCHAR(4) NOT NULL,
  card_brand VARCHAR(50),
  expiry_month INTEGER,
  expiry_year INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: Migrate existing card data to tokens (last 4 digits only)
INSERT INTO payment_tokens (payment_id, token_reference, last_four, card_brand, created_at)
SELECT
  id,
  'TOK_' || MD5(card_number || CURRENT_TIMESTAMP::TEXT),
  RIGHT(card_number, 4),
  'VISA',
  created_at
FROM payments
WHERE card_number IS NOT NULL;

-- Step 3: Remove PCI-DSS prohibited columns
ALTER TABLE payments DROP COLUMN IF EXISTS card_number;
ALTER TABLE payments DROP COLUMN IF EXISTS cvv;
ALTER TABLE payments DROP COLUMN IF EXISTS pin;

-- Step 4: Add token reference to payments
ALTER TABLE payments ADD COLUMN IF NOT EXISTS token_id INTEGER REFERENCES payment_tokens(id);

UPDATE payments p
SET token_id = pt.id
FROM payment_tokens pt
WHERE p.id = pt.payment_id;

-- Step 5: Create indexes
CREATE INDEX IF NOT EXISTS idx_payment_tokens_reference ON payment_tokens(token_reference);
CREATE INDEX IF NOT EXISTS idx_payments_token_id ON payments(token_id);

COMMIT;
EOF

echo "✅ Migration created: migrations/001_remove_pci_violations.sql"

echo ""
echo "→ Updating Payment model..."

cat > "$MODELS_DIR/Payment.js" << 'EOF'
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Payment = sequelize.define('Payment', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  merchant_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  amount: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
  },
  currency: {
    type: DataTypes.STRING(3),
    defaultValue: 'USD',
  },
  status: {
    type: DataTypes.ENUM('pending', 'completed', 'failed'),
    defaultValue: 'pending',
  },
  token_id: {
    type: DataTypes.INTEGER,
    allowNull: true,
    references: {
      model: 'payment_tokens',
      key: 'id',
    },
  },
  created_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
  updated_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'payments',
  timestamps: true,
  underscored: true,
});

module.exports = Payment;
EOF

echo "✅ Payment model updated (CVV/PIN columns removed)"

echo ""
echo "→ Creating PaymentToken model..."

cat > "$MODELS_DIR/PaymentToken.js" << 'EOF'
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const PaymentToken = sequelize.define('PaymentToken', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  payment_id: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
  token_reference: {
    type: DataTypes.STRING(255),
    allowNull: false,
    unique: true,
  },
  last_four: {
    type: DataTypes.STRING(4),
    allowNull: false,
  },
  card_brand: {
    type: DataTypes.STRING(50),
  },
  expiry_month: {
    type: DataTypes.INTEGER,
  },
  expiry_year: {
    type: DataTypes.INTEGER,
  },
  created_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
}, {
  tableName: 'payment_tokens',
  timestamps: false,
  underscored: true,
});

module.exports = PaymentToken;
EOF

echo "✅ PaymentToken model created"

echo ""
echo "→ Creating tokenization service..."

mkdir -p "$BACKEND_DIR/services"

cat > "$BACKEND_DIR/services/tokenization.service.js" << 'EOF'
const crypto = require('crypto');
const PaymentToken = require('../models/PaymentToken');

/**
 * Tokenize card information
 * In production, this would call a PCI-compliant tokenization service (Stripe, Adyen, etc.)
 */
async function tokenizeCard(cardNumber, cvv, expiryMonth, expiryYear) {
  // DEMO ONLY: In production, send to external tokenization service
  const tokenReference = 'TOK_' + crypto.randomBytes(16).toString('hex');
  const lastFour = cardNumber.slice(-4);

  const token = await PaymentToken.create({
    token_reference: tokenReference,
    last_four: lastFour,
    card_brand: detectCardBrand(cardNumber),
    expiry_month: expiryMonth,
    expiry_year: expiryYear,
  });

  return {
    token_id: token.id,
    token_reference: token.token_reference,
    last_four: token.last_four,
  };
}

/**
 * Detokenize card (retrieve from vault)
 * In production, this would call the tokenization service API
 */
async function detokenizeCard(tokenReference) {
  const token = await PaymentToken.findOne({
    where: { token_reference: tokenReference },
  });

  if (!token) {
    throw new Error('Invalid token');
  }

  // In production, this would return the full card details from the vault
  return {
    last_four: token.last_four,
    card_brand: token.card_brand,
    expiry_month: token.expiry_month,
    expiry_year: token.expiry_year,
  };
}

function detectCardBrand(cardNumber) {
  if (cardNumber.startsWith('4')) return 'VISA';
  if (cardNumber.startsWith('5')) return 'MASTERCARD';
  if (cardNumber.startsWith('3')) return 'AMEX';
  return 'UNKNOWN';
}

module.exports = {
  tokenizeCard,
  detokenizeCard,
};
EOF

echo "✅ Tokenization service created"

echo ""
echo "✅ Database schema fixes complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review migration: cat $BACKEND_DIR/migrations/001_remove_pci_violations.sql"
echo "   2. Backup database: pg_dump securebank > backup.sql"
echo "   3. Run migration: psql securebank < migrations/001_remove_pci_violations.sql"
echo "   4. Update payment controller to use tokenization service"
echo "   5. Test payment flow with tokenization"
echo ""
echo "⚠️  IMPORTANT: This migration is IRREVERSIBLE. Backup first!"
