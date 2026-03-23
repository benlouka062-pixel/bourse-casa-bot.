#!/bin/bash
cd ~/bourse_agents
source venv/bin/activate
python agents/calculateur.py
python agents/correlateur_no_numpy.py
python agents/notificateur.py
echo "Exécution terminée à $(date)"
