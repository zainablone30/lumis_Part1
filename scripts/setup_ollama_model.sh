# scripts/setup_ollama_model.sh
ollama create lumis -f ../llm_core/Modelfile
echo "LUMIS model registered in Ollama. Test with: ollama run lumis"