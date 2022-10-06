# FROM acmsolver_env:1.02-slim
FROM  registry.awing.vn/acm-dev/acmsolver_env:1.0
COPY . /acm-cplex-solver/

#Install python requirement libraries
RUN pip install -r /acm-cplex-solver/requirements.txt --no-cache-dir --compile

WORKDIR /acm-cplex-solver/acm_cplex_solver/
CMD ["python", "app.py"]