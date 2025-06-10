export PYTHONPATH=$PYTHONPATH:$(pwd)

python it/polimi/rq2.py multi_victim multi_victim_end 20
python it/polimi/rq2.py multi_victim multi_victim_rescuechild 20
python it/polimi/rq2.py hist with_memory 30
python it/polimi/rq2.py hist with_memory 40
python it/polimi/rq2.py hist with_memory 50