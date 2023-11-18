## Amazon Location Geospatial Agent

This repository provides an example agent that can generate a heatmap of Airbnb listings in New York City when prompted. 
The agent utilizes plan-and-solve prompting with Anthropic's Claude 2 model from Amazon Bedrock.

## Getting Started
First, we need install all dependencies. This agent uses `poetry` to manage dependencies. 
`poetry` is a dependency management and packaging tool for Python.

First, we need to install poetry. If you are on OSX
```bash
brew install poetry
poetry --version
```

If you are on any other OS, [please follow poetry official documentation for installation](https://python-poetry.org/docs/).

Once poetry is installed, we will install all the dependencies using poetry. To install dependencies:
```bash
poetry install
```

Next, lets give the unit tests a run:
```bash
poetry run pytest
```

You can also run unit tests with coverage:

```bash
poetry run coverage run -m pytest 
```

If the tests pass, we are ready to go!

Just in case, there is a Makefile to make our life better. You can also run ```make``` for all of these
```bash
make build
make install
make test
```

## Testing the agent
### Setting up the infra for Amazon Location
Before testing the agent, we will need to create the following the backing AWS account:
1. An Amazon Location Place Index Resource created from Amazon Location Console.
2. An Amazon Location Map Resource created from Amazon Location Console.
3. An Amazon Location API Key created from Amazon Location Console. This API Key should have access permissions to 1 and 2.

After they are created, open `.env` file and set the following env variables:
```env
API_KEY_NAME=<Your Amazon Location API Key of for Places and Maps>
MAP_NAME=<Your Amazon Location Maps resource name>
PLACE_INDEX_NAME=<Your Amazon Location Place Index resource name>
```

As a default, a set of placeholders are used.

### Setting up the infra for AWS Bedrock
Finally, the AWS account we are going to use with the agent MUST have Claude V2 foundational model 
access from Bedrock. At the time of writing, this requires going to Bedrock console and explicitly
clicking a button to ask for access to Claude 2. The request is automatically accepted in a couple of 
moments.

Now we have all the resources we need!

### Using the right credential
The agent runs locally in your machine. Use local AWS credentials that has access to Amazon Bedrock InvokeModel API.
Additionally, it should have access to Amazon Location SearchPlaceIndexForText API.


### Downloading the data
In this sample, we will generate a heatmap from Airbnb database. Download
[the Airbnb 2023 Open Dataset for New York from here](http://data.insideairbnb.com/united-states/ny/new-york-city/2023-10-01/visualisations/listings.csv).
Store the file inside the `data` folder.

```bash
wget http://data.insideairbnb.com/united-states/ny/new-york-city/2023-10-01/visualisations/listings.csv
cp listings.csv data/listings.csv
```

Then run the following to crete a session. We are using a guid named `3c18d48c-9c9b-488f-8229-e2e8016fa851` 
as example session id. This will create a session with `listings.csv` stored inside `data` folder.

```bash
SESSION_ID="3c18d48c-9c9b-488f-8229-e2e8016fa851" FILE_NAME="listings.csv" make create-session
```

### Starting the agent
The agent can run inside a docker container or outside docker container. We recommend running the agent inside a docker container. 
This way, the generated code can not create any unexpected side effect.

We can build the docker image for the agent by:

```bash
docker build -t agent .
```

Then, we can shell into docker by:

```bash
docker run --rm -it -v ~/.aws:/root/.aws --entrypoint bash agent
```

Then, start the agent using inside docker:
```bash
poetry run agent --session-id 3c18d48c-9c9b-488f-8229-e2e8016fa851
```

If you want to use an AWS profile, there is a `--profile` flag available
```bash
poetry run agent --session-id 3c18d48c-9c9b-488f-8229-e2e8016fa851 --profile some-aws-profile
```

The agent will write all generated content under `geospatial-agent-session-storage` folder.

Now, when prompted by the agent, we can use the following input to generate the heatmap.
```
I've uploaded the file listings.csv. Draw a heatmap of Airbnb listing price.
```

And then, let the agent do its thing!

### Limitations
This agent can work on datasets other than the one used for training, but its performance is not guaranteed to be perfect 
on all datasets and tasks.

The agent can generate high-level plans to solve problems. However, to translate those plans into executable code, 
it relies on the Claude 2 model which is good at writing Python code using built-ins but has limitations. 
Claude 2 scored 74% on the HumanEval Python test.

To reliably write code dealing with geospatial data, the agent would need additional training focused on libraries 
like geopandas, matplotlib, and pydeck. In particular, knowledge of geopandas is crucial for spatial joins.

While the agent can plan spatial joins, it often fails to write functioning geopandas code to join columns from two 
dataframes. Common issues include data type mismatches and coordinate system incompatibilities. We tried addressing 
these with prompting, but without further tuning or a model specialized for geopandas, success rates across diverse 
datasets will be limited.