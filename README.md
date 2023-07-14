## Amazon Location Geospatial Agent

Amazon Location Geospatial Agent is an autonomous agent built with the power of LLMs. This agent uses Amazon Bedrock
model Anthropic Claude 2 as its primary model. It is a Plan and Solve agent. 

[This internal blog link sheds more light on what we this agent has achieved.](https://console.harmony.a2z.com/ifelse/blog/Plan%20and%20solve%20agents/2023-08-08%20-%20Plan%20and%20Solve%20Agents.html).
This guide is about how to test this agent. This version of the agent only runs locally through a command-line-interface (CLI).

## Getting Started
First, we need install all dependencies. This is not a Brazilified package. This agent uses `poetry` to manage dependencies. 
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

After they are created, open the `Makefile` and under `.EXPORT_ALL_VARIABLES:` sections, set the following env variables:
```makefile
.EXPORT_ALL_VARIABLES:
API_KEY_NAME=AgentAPIKey
MAP_NAME=AgentMap
PLACE_INDEX_NAME=AgentPlaceIndex
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

### Starting the agent
The agent runs locally and needs a local session store. We will see that soon in action. Furthermore, the agent
can run inside docker or outside docker. We recommend running the agent inside a docker container because it 
generates code. And to keep the user environment safe for any unexpected side effect, docker is used.

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
poetry run agent
```

With these commands we have not given the agent a session id. A session id is a GUID the agent uses
to keep all data and generated content for a session inside a folder. After you invoke the session,
you will see a folder named `geospatial-agent-session-storage` being created.

Inside this folder, there will be sub-folder for each session. If you want to create a session yourself
use:

```bash
SESSION_ID="3c18d48c-9c9b-488f-8229-e2e8016fa851" make create-session
```

I used `3c18d48c-9c9b-488f-8229-e2e8016fa851` as a placeholder. You can use your own session id.

For our testing run we will generate a heatmap from Airbnb database. To do that, we will have to copy
`data/airbnb_listings_price.csv` to the `data` subfolder under the session folder.

For example in this case, that folder will be `geospatial-agent-session-storage/3c18d48c-9c9b-488f-8229-e2e8016fa851/data`.
After copying `data/airbnb_listings_price.csv` to this folder we can ask the agent to create a heatmap by putting 
this input:

```
I've uploaded the file airbnb_listings_price.csv. Draw a heatmap of Airbnb listing price
```

And then, let the agent do it's thing!
