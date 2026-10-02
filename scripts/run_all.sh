# scripts/run_all.sh
#!/bin/bash
ollama serve &
uvicorn backend.main:app --reload --port 8000 &
uvicorn avatar_3d.avatar_server:app --port 8100 &
streamlit run frontend_dashboard/app.py --server.port 8501 &
streamlit run therapist_dashboard/dashboard_app.py --server.port 8502