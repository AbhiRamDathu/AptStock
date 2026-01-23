# 🚀 ForecastAI Pro - Pre-Deployment Checklist

## Backup & Monitoring Verification

### Before Launching to First Customer (Dec 20-24)

- [ ] **MongoDB Atlas Configured**
  - [ ] Email alerts set up for: Database Down, High Connections
  - [ ] Manual baseline snapshot taken: "pre-launch-baseline-dec17-2025"
  - [ ] Test alert email received

- [ ] **Local Backup Script Installed**
  - [ ] `scripts/backup_mongodb.sh` created and tested
  - [ ] Run it manually once: `./scripts/backup_mongodb.sh`
  - [ ] Verify backup file created in `./backups/mongodb/`
  - [ ] Cron job configured to run daily/weekly

- [ ] **Database Monitoring Added**
  - [ ] `database_service.py` extended with monitoring methods
  - [ ] `/api/admin/health` endpoint created and tested
  - [ ] `audit_logs` collection configured

- [ ] **Action Logging Implemented**
  - [ ] Login/logout actions logged in `audit_logs`
  - [ ] File upload actions logged
  - [ ] Can view user activity via `/api/admin/user-activity/{user_id}`

- [ ] **Backup Restore Test**
  - [ ] [ ] Create a test backup using `mongodump`
  - [ ] [ ] Delete a test collection
  - [ ] [ ] Restore from backup to confirm it works
  - [ ] [ ] Document restore procedure

### Ongoing (Weekly/Monthly)

- [ ] Check backup logs: `cat logs/backup.log`
- [ ] Verify latest backup file exists in `./backups/mongodb/`
- [ ] Test restore procedure monthly
- [ ] Check `/api/admin/health` returns `"status": "healthy"`

### Disaster Recovery (If DB Issue)

**Step 1: Diagnose**
curl http://localhost:8000/api/admin/health


**Step 2: Check Recent Backup**
ls -lh ./backups/mongodb/

**Step 3: Restore If Needed**
Stop app
Restore backup
mongorestore --uri="$MONGO_URI" ./backups/mongodb/latest/apdf_io_mongo/

Restart app
undefined