# test03

## container environment

This notebook can be served from a containerized environment if desired:

 - `docker image build -t nb .`
 - `docker container run -p 8888:8888 -v $(pwd):/books nb`
 - Visit the notebook URL provided and run as usual.