# MED-EXPIRY V3: Cloud Deployment & Security Guide
(Features 21, 23, 24)

## ☁️ Deployment Reference: AWS / Azure / GCP

The application is architected for containerized deployment (Docker) to ensure scalability across multi-store branches.

### Recommended Infrastructure
- **Server**: AWS EC2 t3.medium or Azure B2s (Python/Flask backend).
- **Database**: Amazon RDS (PostgreSQL) for high-availability medicine data.
- **Storage**: Amazon S3 for Medicine Image preservation.
- **CDN**: CloudFront for low-latency frontend delivery.

### 🛡️ Security Hardening (Feature 23)
1. **JWT Authentication**: All REST API calls require a valid Bearer token.
2. **Password Entropy**: Passwords are multi-salted and hashed via SHA-256.
3. **Role-Based Access (RBAC)**: Fine-grained permissions (Admin, Staff, Observer).
4. **Data Isolation**: Multi-store branches are logically isolated via `branch_id` filters.

### 💾 Backup Strategy
- **Automated Snaphots**: Nightly database snapshots with 30-day retention.
- **Audit Logs**: Activity logs are immutable and stored in a separate audit-db.
- **Point-in-Time Recovery**: Enabled for the RDS instance to prevent data loss.

### 🤖 Future AI Integration (Feature 24)
- **Demand Forecasting**: Integrated TensorFlow models to predict medicine restock needs.
- **Intelligent Pricing**: Real-time pricing adjustments based on shelf-life proximity.
- **Expiry Risk Score**: Calculated on-the-fly based on category and storage conditions.
