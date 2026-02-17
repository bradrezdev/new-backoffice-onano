# NNProtect Backoffice & E-commerce Platform

**Project Manager Report - Current Implementation Status**

This document provides a comprehensive overview of the `NNProtect_new_website` project, detailing its current architecture, technology stack, and implemented features as of February 2026. This project acts as a centralized Backoffice and E-commerce solution for a Multi-Level Marketing (MLM) organization.

## 🏗 Project Overview

The **NNProtect_new_website** is a robust, full-stack web application built using **Reflex (Python)**. It integrates advanced MLM functionalities with a complete E-commerce store, providing a seamless experience for affiliates and administrators. The system is designed to handle complex compensation plans, real-time network genealogy, order processing, and financial management through a digital wallet system.

## 🚀 Tech Stack

*   **Framework**: [Reflex](https://reflex.dev/) (Full-stack Python web framework)
*   **Database ORM**: **SQLModel** (Recently migrated from pure SQLAlchemy to standard SQLModel for better type safety)
*   **Database Migrations**: **Alembic**
*   **Database Engine**: PostgreSQL (implied via `psycopg2` / `SQLAlchemy`)
*   **Styling**: Tailwind CSS (Rx plugin)
*   **Task Scheduling**: APScheduler (for periodic tasks like commission calculations)

## 🏛 Architecture

The project has undergone a significant architectural refactor to improve scalability and maintainability. It now follows a **Modular Architecture**, moving away from a monolithic service structure.

### 1. Modular Structure (`NNProtect_new_website/modules/`)
The application logic and UI pages are organized by domain:
*   **`auth/`**: Authentication, Registration (with/without sponsor), and User Management.
*   **`network/`**: MLM specific logic - Genealogy, Tree Views, and Team Reports.
*   **`store/`**: E-commerce functionality - Products, Cart, Orders, Payment, and Shipping.
*   **`finance/`**: Financial operations - Wallet, Withdrawals, and Income Reports.
*   **`admin/`**: Administrative interfaces for system management.

### 2. Database Layer (`database/`)
The data layer is centralized, with individual model files defining the schema using **SQLModel**:
*   **Users & Auth**: `users.py`, `roles.py`, `auth_credentials.py`, `userprofiles.py`.
*   **Network (MLM)**: `ranks.py`, `periods.py`, `usertreepaths.py`, `user_rank_history.py`.
*   **Commerce**: `products.py`, `orders.py`, `order_items.py`, `addresses.py`.
*   **Finance**: `comissions.py`, `wallet.py`, `cashback.py`, `loyalty_points.py`, `travel_campaigns.py`.

## ✨ Key Features Implemented

### 🔐 Authentication & Compliance
*   **Login/Register**: Secure authentication flows.
*   **Sponsorship**: Registration logic handling referral links and sponsor assignment.
*   **Role-Based Access Control (RBAC)**: Defined in `roles.py`.

### 🌐 Network Marketing (MLM)
*   **Genealogy Tracking**: Implements complex tree structures to track upline/downline relationships.
*   **Rank System**: Dynamic rank calculation and history tracking (`ranks.py`).
*   **Commissions Engine**: Comprehensive bonus calculation including:
    *   Direct Bonus
    *   Fast Start Bonus
    *   Unilevel Bonus
    *   Matching Bonus
    *   Rank Achievement Bonus
*   **Period Management**: Handling of commission periods (Monthly/Weekly).

### 🛒 E-commerce Store
*   **Product Catalog**: Management of products with active ingredients.
*   **Shopping Cart**: Fully functional cart and checkout process.
*   **Order Management**: State machine for order lifecycle (Pending -> Paid -> Shipped).

### 💰 Financial System & Wallet
*   **Digital Wallet**: Each user has a `Wallets` record for managing funds.
*   **Transaction Management**: `WalletTransaction` tracks all credits (Commissions) and debits (Withdrawals, Purchases).
*   **Withdrawals**: Feature for affiliates to request payouts.
*   **Incentives**:
    *   **Loyalty Points**: Rewards for consistent activity.
    *   **Travel Campaigns**: Tracking for incentive trips.
    *   **Cashback**: Purchase rewards system.
    
### 💰 MLM Ranks
* **id: 1 -> ´Sin rango´**: 0 PV (personal volume/volumen personal) + 0 GV (grupal volume/volumen grupal)
* **id: 2 -> ´Bronce**: 100 PV (personal volume/volumen personal) + 1000 GV (grupal volume/volumen grupal)
* **id: 3 -> Plata**: 100 PV (personal volume/volumen personal) + 3000 GV (grupal volume/volumen grupal)
* **id: 4 -> Oro**: 100 PV (personal volume/volumen personal) + 5000 GV (grupal volume/volumen grupal)
* **id: 5 -> Platino**: 100 PV (personal volume/volumen personal) + 10000 GV (grupal volume/volumen grupal)
* **id: 6 -> Diamante**: 100 PV (personal volume/volumen personal) + 25000 GV (grupal volume/volumen grupal)
* **id: 7 -> Doble Diamante**: 100 PV (personal volume/volumen personal) + 50000 GV (grupal volume/volumen grupal)
* **id: 8 -> Triple Diamante**: 100 PV (personal volume/volumen personal) + 100000 GV (grupal volume/volumen grupal)
* **id: 9 -> Diamante Embajador**: 100 PV (personal volume/volumen personal) + 250000 GV (grupal volume/volumen grupal)
* **id: 10 -> Doble Diamante Embajador**: 100 PV (personal volume/volumen personal) + 500000 GV (grupal volume/volumen grupal)
* **id: 11 -> Triple Diamante Embajador**: 100 PV (personal volume/volumen personal) + 1000000 GV (grupal volume/volumen grupal)


## 🔄 Recent Refactors & Improvements

1.  **SQLModel Migration**: The entire database layer was migrated to **SQLModel**, standardizing the ORM and simplifying data validation.
2.  **Modular UI**: React/Reflex components have been refactored into domain-specific modules.
3.  **Connection Pooling**: Implemented a fix in `rxconfig.py` (`_get_db_engine_with_pool`) to handle database connections more efficiently and prevent timeouts.
4.  **Functional Components**: Modernization of UI components (e.g., `components/inputs.py`) towards a functional paradigm.

## 📁 Repository Structure

```
NNProtect_new_website/
├── alembic/                # Database migrations
├── assets/                 # Static assets (images, icons)
├── database/               # SQLModel database definitions
├── NNProtect_new_website/  # Main Application Source
│   ├── modules/            # Domain-driven modules (auth, store, network, etc.)
│   ├── components/         # Shared UI components
│   └── NNProtect_new_website.py # App entry point
├── rxconfig.py             # Reflex configuration
└── requirements.txt        # Python dependencies
```

---
*Last Updated: 16 de febrero de 2026*
