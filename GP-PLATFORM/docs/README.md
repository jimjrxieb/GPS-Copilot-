# GP-CONFIG-OPS - Configuration & Documentation Hub

**Purpose**: Centralized configuration management and living documentation for GP-Copilot platform.

---

## 📂 Directory Structure

### **Architecture Documentation** (Living Docs)
- `SECURITY_ARCHITECTURE_GUIDE.md` - Complete security architecture reference
- `SCANNER_ARCHITECTURE_DOCUMENTATION.md` - Scanner tooling architecture and patterns
- `JAMES_SECURITY_QUICK_REFERENCE.md` - Quick reference commands and workflows

### **Configuration**
- `GP-config/` - Platform configuration files and settings
- `backups/` - Configuration backups and restore points

### **Operational Scripts**
- `gp_status.py` - Platform health check and status reporting
- `demo_client_showcase.py` - Client demonstration automation
- `demo_infrastructure_automation_standalone.py` - Infrastructure automation demo
- `import_fix.py` - Import path resolution utility

---

## 🎯 Purpose

GP-CONFIG-OPS serves as the **operational control center** for configuration and documentation:

1. **Living Documentation**: Up-to-date architecture guides and references
2. **Configuration Management**: Platform settings and config files
3. **Operational Scripts**: Status monitoring and demo automation
4. **Config Backups**: Configuration version control and recovery

---

## 🔗 Integration Points

### **With GP-CONSULTING-AGENTS**:
- Provides configuration for scanners and agents
- Operational scripts for platform management

### **With GP-DATA**:
- All scan results, analysis, and historical data stored in GP-DATA
- GP-CONFIG-OPS contains NO scan results or outputs

### **With James Brain**:
- Status reporting via `gp_status.py`
- Demo automation for client showcases

---

## 🚀 Key Commands

### Platform Status Check
```bash
cd GP-CONFIG-OPS
python3 gp_status.py
```

### Client Demo Execution
```bash
python3 demo_client_showcase.py
```

---

## 📋 What Belongs Here

**✅ KEEP:**
- Living architecture documentation
- Platform configuration files
- Operational/demo scripts
- Config backups

**❌ MOVE TO GP-DATA:**
- Scan results (→ GP-DATA/active/scans/)
- Analysis reports (→ GP-DATA/active/analysis/)
- Historical assessments (→ GP-DATA/archive/docs/)
- Session summaries (→ GP-DATA/archive/docs/)
- Client engagement data (→ GP-DATA/archive/engagements/)

---

**Status**: Production Ready | Clean configuration and documentation hub