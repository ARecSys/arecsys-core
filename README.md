# arecsys-core
Propose articles according to recommandation algorithms.

# Code Structure
```
Arecsys-core
└── algofst
│   ├── __init__.py        # Load credentials and password to the database
│   ├── function.json      # queue initialization
│   └── sample.dat         # begin the queue if needed
|
└── deprecated             # Dockerfiles
|
└── src
│   ├── algo.py            # Functions of the recommendation algorithm
│   ├── app.py             # App that, for the moment print the results of the fct algofst on the route/doi
│   ├── send_msg.py        # Message to the Queue
│   └── results.py         # backend compute of recommendation and publishing into a database
```
