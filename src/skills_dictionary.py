"""Skills dictionary. Mirror of notebooks/04_skills_extract.py; the
GitHub Actions pipeline (src/pipeline.py) uses this copy."""

SKILLS = {
 "sql":        {"cat": "language",   "aliases": [r"\bsql\b"]},
 "python":     {"cat": "language",   "aliases": [r"\bpython\b"]},
 "scala":      {"cat": "language",   "aliases": [r"\bscala\b"]},
 "java":       {"cat": "language",   "aliases": [r"\bjava\b(?!script)"]},
 "javascript": {"cat": "language",   "aliases": [r"\bjavascript\b"]},
 "php":        {"cat": "language",   "aliases": [r"\bphp\b"]},
 "r_lang":     {"cat": "language",   "aliases": [
                    r"(?<=[ ,/(])r(?=[ ,/)])"]},


 "spark":      {"cat": "processing", "aliases": [r"\bapache spark\b",
                                                 r"\bpyspark\b",
                                                 r"\bspark\b"]},
 "hadoop":     {"cat": "legacy",     "aliases": [r"\bhadoop\b",
                                                 r"\bhdfs\b",
                                                 r"\bmapreduce\b",
                                                 r"\bhive\b"]},
 "kafka":      {"cat": "streaming",  "aliases": [r"\bkafka\b"]},
 "flink":      {"cat": "streaming",  "aliases": [r"\bflink\b"]},


 "databricks": {"cat": "platform",   "aliases": [r"\bdatabricks\b"]},
 "snowflake":  {"cat": "warehouse",  "aliases": [r"\bsnowflake\b"]},
 "bigquery":   {"cat": "warehouse",  "aliases": [r"\bbigquery\b"]},
 "redshift":   {"cat": "warehouse",  "aliases": [r"\bredshift\b"]},
 "synapse":    {"cat": "warehouse",  "aliases": [r"\bsynapse\b"]},


 "airflow":    {"cat": "orchestr",   "aliases": [r"\bapache airflow\b",
                                                 r"\bairflow\b"]},
 "dbt":        {"cat": "transform",  "aliases": [r"\bdbt\b"]},
 "ssis":       {"cat": "legacy",     "aliases": [r"\bssis\b"]},
 "talend":     {"cat": "legacy",     "aliases": [r"\btalend\b"]},


 "postgres":   {"cat": "database",   "aliases": [r"\bpostgresql\b",
                                                 r"\bpostgres\b"]},
 "mysql":      {"cat": "database",   "aliases": [r"\bmysql\b"]},
 "mssql":      {"cat": "database",   "aliases": [r"\bsql server\b",
                                                 r"\bt-sql\b",
                                                 r"\bms sql\b"]},
 "oracle":     {"cat": "database",   "aliases": [r"\boracle\b"]},
 "mongodb":    {"cat": "database",   "aliases": [r"\bmongodb\b",
                                                 r"\bmongo\b"]},
 "elastic":    {"cat": "database",   "aliases": [r"\belasticsearch\b"]},


 "aws":        {"cat": "cloud",      "aliases": [r"\baws\b",
                                                 r"\bamazon web services\b"]},
 "azure":      {"cat": "cloud",      "aliases": [r"\bazure\b",
                                                 r"\bdata factory\b"]},
 "gcp":        {"cat": "cloud",      "aliases": [r"\bgcp\b",
                                                 r"\bgoogle cloud\b"]},


 "docker":     {"cat": "devops",     "aliases": [r"\bdocker\b"]},
 "kubernetes": {"cat": "devops",     "aliases": [r"\bkubernetes\b",
                                                 r"\bk8s\b"]},
 "terraform":  {"cat": "devops",     "aliases": [r"\bterraform\b"]},
 "git":        {"cat": "devops",     "aliases": [r"\bgithub\b",
                                                 r"\bgitlab\b",
                                                 r"\bgit\b"]},
 "cicd":       {"cat": "devops",     "aliases": [r"\bci/cd\b",
                                                 r"\bjenkins\b"]},


 "powerbi":    {"cat": "bi",         "aliases": [r"\bpower ?bi\b"]},
 "tableau":    {"cat": "bi",         "aliases": [r"\btableau\b"]},
 "looker":     {"cat": "bi",         "aliases": [r"\blooker\b"]},
 "qlik":       {"cat": "bi",         "aliases": [r"\bqlik\b"]},
 "excel":      {"cat": "bi",         "aliases": [r"\bexcel\b"]},


 # --- ML frameworks: how a model gets trained -----------------
 "pytorch":    {"cat": "ml_framework", "aliases": [r"\bpytorch\b"]},
 "tensorflow": {"cat": "ml_framework", "aliases": [r"\btensorflow\b"]},
 "keras":      {"cat": "ml_framework", "aliases": [r"\bkeras\b"]},
 "sklearn":    {"cat": "ml_framework", "aliases": [r"\bscikit-?learn\b",
                                                   r"\bsklearn\b"]},
 "xgboost":    {"cat": "ml_framework", "aliases": [r"\bxgboost\b",
                                                   r"\blightgbm\b",
                                                   r"\bcatboost\b"]},
 "jax":        {"cat": "ml_framework", "aliases": [r"\bjax\b"]},

 # --- MLOps: how a model reaches production -------------------
 # Kept separate from ml_framework because these are the skills
 # that separate "trained a model in a notebook" from "runs a
 # model as a service", and that gap is the whole MLOps story.
 "mlflow":     {"cat": "mlops",      "aliases": [r"\bmlflow\b"]},
 "kubeflow":   {"cat": "mlops",      "aliases": [r"\bkubeflow\b"]},
 "sagemaker":  {"cat": "mlops",      "aliases": [r"\bsagemaker\b",
                                                 r"\bsage maker\b"]},
 "vertexai":   {"cat": "mlops",      "aliases": [r"\bvertex ai\b",
                                                 r"\bvertex\b"]},
 "azureml":    {"cat": "mlops",      "aliases": [r"\bazure ml\b",
                                                 r"\bazure machine "
                                                 r"learning\b",
                                                 r"\bazure ai foundry\b"]},
 "ray":        {"cat": "mlops",      "aliases": [r"\bray serve\b",
                                                 r"\bray\.io\b",
                                                 r"\banyscale\b"]},
 "wandb":      {"cat": "mlops",      "aliases": [r"\bweights ?& ?biases\b",
                                                 r"\bwandb\b"]},
 "bentoml":    {"cat": "mlops",      "aliases": [r"\bbentoml\b",
                                                 r"\bseldon\b",
                                                 r"\btriton\b",
                                                 r"\bkserve\b"]},
 "featurestore": {"cat": "mlops",    "aliases": [r"\bfeature store\b",
                                                 r"\bfeast\b",
                                                 r"\btecton\b"]},

 # --- Generative AI -------------------------------------------
 # "llm" and "rag" used to be aliases of one skill, which made it
 # impossible to see whether DACH employers are asking for models
 # or for retrieval on top of them. They are now separate.
 "llm":        {"cat": "genai",      "aliases": [r"\bllms?\b",
                                                 r"\blarge language "
                                                 r"models?\b",
                                                 r"\bsprachmodell\w*\b",
                                                 r"\bfoundation models?\b"]},
 "genai":      {"cat": "genai",      "aliases": [r"\bgenai\b",
                                                 r"\bgen[\s\-]?ai\b",
                                                 r"\bgenerative ai\b",
                                                 r"\bgenerative ki\b"]},
 "rag":        {"cat": "genai",      "aliases": [r"\bretrieval[\s\-]"
                                                 r"augmented\w*\b",
                                                 r"\brag\b"]},
 "ai_agents":  {"cat": "genai",      "aliases": [r"\bagentic\b",
                                                 r"\bai agents?\b",
                                                 r"\bki[\s\-]agenten?\b",
                                                 r"\bmulti[\s\-]agent\b",
                                                 r"\bmcp\b"]},
 "prompting":  {"cat": "genai",      "aliases": [r"\bprompt[\s\-]?"
                                                 r"engineer\w*\b",
                                                 r"\bprompting\b"]},
 "langchain":  {"cat": "genai",      "aliases": [r"\blangchain\b",
                                                 r"\blanggraph\b",
                                                 r"\bllama[\s\-]?index\b",
                                                 r"\bsemantic kernel\b",
                                                 r"\bhaystack\b"]},
 "huggingface": {"cat": "genai",     "aliases": [r"\bhugging ?face\b",
                                                 r"\btransformers "
                                                 r"library\b"]},
 "openai_api": {"cat": "genai",      "aliases": [r"\bopenai\b",
                                                 r"\bgpt-?[45]\b",
                                                 r"\banthropic\b",
                                                 # not bare "Claude":
                                                 # it is a first name
                                                 # in Swiss postings
                                                 r"\bclaude (api|sonnet|"
                                                 r"opus|code)\b",
                                                 r"\bazure openai\b",
                                                 r"\bmistral\b",
                                                 r"\bgemini\b"]},
 "vectordb":   {"cat": "genai",      "aliases": [r"\bvector (db|"
                                                 r"database|store)\b",
                                                 r"\bvektordatenbank\b",
                                                 r"\bpinecone\b",
                                                 r"\bweaviate\b",
                                                 r"\bqdrant\b",
                                                 r"\bmilvus\b",
                                                 r"\bchroma\b",
                                                 r"\bpgvector\b",
                                                 r"\bfaiss\b"]},
 "finetuning": {"cat": "genai",      "aliases": [r"\bfine[\s\-]?tun\w*\b",
                                                 # LoRaWAN is an IoT
                                                 # radio protocol and
                                                 # shows up in DACH
                                                 # embedded postings
                                                 r"\blora\b(?!wan)",
                                                 r"\bpeft\b",
                                                 r"\brlhf\b",
                                                 r"\bembeddings?\b"]},
 "ai_eval":    {"cat": "genai",      "aliases": [r"\bllm[\s\-]?as[\s\-]?"
                                                 r"a[\s\-]?judge\b",
                                                 r"\bhallucination\w*\b",
                                                 r"\bguardrails?\b",
                                                 r"\bevals?\b",
                                                 r"\bai safety\b",
                                                 r"\bai alignment\b"]},

 # --- NLP and computer vision ---------------------------------
 "nlp":        {"cat": "nlp_cv",     "aliases": [r"\bnlp\b",
                                                 r"\bnatural language "
                                                 r"processing\b",
                                                 r"\bsprachverarbeitung\b",
                                                 r"\bspacy\b",
                                                 r"\bnltk\b"]},
 "cv":         {"cat": "nlp_cv",     "aliases": [r"\bcomputer vision\b",
                                                 r"\bbildverarbeitung\b",
                                                 r"\bbilderkennung\b",
                                                 r"\bopencv\b",
                                                 r"\byolo\b",
                                                 r"\bobject detection\b"]},
 "deeplearning": {"cat": "nlp_cv",   "aliases": [r"\bdeep learning\b",
                                                 r"\bneural network\w*\b",
                                                 r"\bneuronale netze\b",
                                                 r"\btransformer\b",
                                                 r"\bdiffusion model\w*\b"]},


 # --- software engineering ------------------------------------
 "typescript": {"cat": "language",   "aliases": [r"\btypescript\b"]},
 "golang":     {"cat": "language",   "aliases": [r"\bgolang\b",
                                                 r"\bgo \(golang\)"]},
 "csharp":     {"cat": "language",   "aliases": [r"\bc#", r"\.net\b",
                                                 r"\bdotnet\b"]},
 "cpp":        {"cat": "language",   "aliases": [r"\bc\+\+"]},
 "kotlin":     {"cat": "language",   "aliases": [r"\bkotlin\b"]},
 "rust":       {"cat": "language",   "aliases": [r"\brust\b"]},
 "react":      {"cat": "frontend",   "aliases": [r"\breact(\.?js)?\b"
                                                 r"(?! native)"]},
 "angular":    {"cat": "frontend",   "aliases": [r"\bangular(js)?\b"]},
 "vue":        {"cat": "frontend",   "aliases": [r"\bvue(\.?js)?\b"]},
 "nodejs":     {"cat": "backend",    "aliases": [r"\bnode\.?js\b"]},
 "spring":     {"cat": "backend",    "aliases": [r"\bspring boot\b",
                                                 r"\bspring framework\b"]},
 "django":     {"cat": "backend",    "aliases": [r"\bdjango\b",
                                                 r"\bfastapi\b",
                                                 r"\bflask\b"]},
 # SWIFT is also the bank messaging network
 "swift":      {"cat": "mobile",     "aliases": [r"\bswiftui\b",
                                                 r"\bswift\b(?![\s\-]"
                                                 r"?(mt|mx|messag|network|"
                                                 r"code|zahlung|payment))"]},
 "react_native": {"cat": "mobile",   "aliases": [r"\breact native\b"]},
 "flutter":    {"cat": "mobile",     "aliases": [r"\bflutter\b"]},
 "ansible":    {"cat": "devops",     "aliases": [r"\bansible\b"]},

 "sap":        {"cat": "enterprise", "aliases": [r"\bsap\b"]},
 "etl":        {"cat": "practice",   "aliases": [r"\betl\b", r"\belt\b"]},
 "datawarehouse": {"cat": "practice", "aliases": [
                    r"\bdata warehouse\b", r"\bdwh\b",
                    r"\bdata lakehouse\b", r"\bdata lake\b"]},
}

CATEGORY = {k: v["cat"] for k, v in SKILLS.items()}
