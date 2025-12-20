# Distress Property Detector 🏠📉

A web-based platform that identifies real estate properties listed for distress sale by analyzing pricing, descriptions, and market trends. The system generates a **distress score** to help investors and buyers quickly identify high-potential opportunities.

---

## 🚀 Features

- **Property Data Ingestion**
  - CSV uploads
  - API-based imports
  - Manual entry

- **Distress Scoring Algorithm**
  - Price deviation vs market averages
  - Keyword detection (e.g., *urgent*, *auction*, *must sell*)
  - Weighted scoring model

- **Interactive Dashboard**
  - Filter by location, price, distress score
  - Sortable property tables

- **User Accounts**
  - Authentication & profiles
  - Save favorite properties

- **Notifications**
  - Email alerts (SendGrid)
  - SMS alerts (Twilio)

- **Data Visualization**
  - Market trend charts
  - Distress heatmaps using Google Maps

---

## 🛠 Tech Stack

### Backend
- Django
- Django REST Framework
- PostgreSQL
- Pandas / Scikit-learn

### Frontend
- React
- Tailwind CSS
- Chart.js / Plotly

### Integrations
- Google Maps API
- Twilio API
- SendGrid API

---

## 📂 Project Structure


---

## 🔐 API Endpoints

### Authentication
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`

### Properties
- `GET /api/properties`
- `GET /api/properties/{id}`
- `POST /api/properties`
- `PUT /api/properties/{id}`
- `DELETE /api/properties/{id}`

### Favorites
- `GET /api/favorites`
- `POST /api/favorites/{property_id}`
- `DELETE /api/favorites/{property_id}`

### Notifications
- `GET /api/notifications`
- `POST /api/notifications`
- `PUT /api/notifications/{id}`
- `DELETE /api/notifications/{id}`

---

## 🗓 Project Timeline

- **Week 1:** Project setup & data modeling
- **Week 2:** Distress scoring algorithm
- **Week 3:** Dashboard UI
- **Week 4:** User accounts & notifications
- **Week 5:** Visualizations & deployment

---

## 🧪 Testing
- Unit tests for scoring logic
- API endpoint validation
- CSV ingestion validation

---

## 🌍 Deployment
- Render / Railway
- PostgreSQL database
- Environment variables for secrets

---

