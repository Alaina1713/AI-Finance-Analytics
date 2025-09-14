# Objective / Purpose

Develop an end-to-end machine learning platform for financial market data, enabling real-time and batch analytics for investment decision-making. The system focuses on efficient data ingestion, model training, deployment, and monitoring for financial analytics pipelines.

# Tools & Technologies Used

- Programming & ML: Python, Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch
- Data Pipelines & Orchestration: Airflow, Kafka, Spark, SQL
- Platform & Deployment: Kubernetes (K8s), Kubeflow, CI/CD pipelines
- Model Serving: Triton, torchserve, BentoML, ONNX
- Visualization & Reporting: Power BI, Matplotlib

# Methodology / Architecture

- Data Ingestion: Streaming and batch financial market data pipelines for stocks and crypto using Kafka + Spark.
- Data Processing: Cleaning, transformation, and feature engineering in scalable Python pipelines.
- Model Training: LSTM and other ML models trained on real-time and historical data using Kubeflow + K8s.
- Model Deployment & Monitoring: Automated deployment via CI/CD pipelines; real-time model monitoring for latency and performance metrics.
- Integration: Outputs integrated with dashboards for investment insights and decision support.

# Key Results

- Delivered low-latency analytics pipelines for both real-time and batch market data.
- Achieved accurate investment insights, integrated into dashboards for actionable decision-making.
- Built a scalable, end-to-end ML platform that mirrors production-grade financial systems.


1️⃣ Clone the Repository
cd AI-Finance-Analytics

2️⃣ Setup Virtual Environment
cd backend

python -m venv venv
source venv/bin/activate # (Linux/Mac)
venv\Scripts\activate # (Windows)

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Flask Server
python app.py

Server runs at: http://127.0.0.1:5000/

5️⃣ View Frontend

Open http://127.0.0.1:5000/ in your browser.

🧪 Example Use Cases
 - Upload your monthly financial data (CSV/Excel).
 - View Revenue Growth, Retention, GMV, and Profit margins.
 - Predict next quarter’s financial trends using ML models.
 - Run SQL queries directly from the dashboard.

🔮 Future Enhancements

✅ Integration with Mixpanel/Amplitude for product analytics.

✅ Real-time streaming data using Kafka.

✅ Deploy with Docker + AWS RDS + EC2.
