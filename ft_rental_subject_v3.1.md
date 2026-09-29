**# ft\_rental\_architecture**

**### Distributed Booking Engine & Event-Driven Systems**

**\*\*Version: 3.0 (final)\*\***

\---

**## Chapter 1 — Preamble**

Imagine a popular rental platform during a holiday weekend. Two distinct users, separated by thousands of miles, click the "Reserve" button on the exact same asset at the exact same millisecond.

If your backend is a standard, naive CRUD application, your database will silently write both records. You have just double-booked an asset. Your company loses money, customer trust evaporates, and the operations team bears the burden.

To survive, you must abandon naive read-then-write logic and embrace relational range types, row-level pessimistic locking, explicit transaction boundaries, and asynchronous webhook-verified payment confirmation — all wrapped in a security posture that assumes every external input is hostile until proven otherwise.

It is time to architect a system that does not break under pressure, and does not bend under attack.

\---

**## Chapter 2 — Architecture Overview**

A single backend service, fronted by a reverse proxy, talking to PostgreSQL and Redis. The frontend is served separately.

The request path:

\`\`\`

client (React)

   │

   ▼

nginx (reverse proxy — public, the only container with a published port)

   │

   ▼

FastAPI backend (private — internal Docker network only)

   │

   ├──▶ PostgreSQL  (Users, Assets, Bookings — GiST index on date ranges)

   └──▶ Redis       (distributed checkout lock + cache)

\`\`\`

**\*\*Requirements:\*\***

\- The backend container must never have a published port mapped to the host. Only nginx is reachable from outside the Docker network.

\- Every request — from the browser, from Stripe's webhook, from anything external — must pass through nginx first. There is no second path into the system.

\- The repository includes a Makefile at the root wrapping all common Docker Compose operations (\`build\`, \`up\`, \`down\`, \`logs\`, \`test\`, \`seed\`, \`clean\`) so the project can be started, tested, and torn down without memorizing raw \`docker-compose\` invocations.

\- Any logic requiring real branching (environment setup, health-check waiting, data seeding) lives in a script called from a Makefile target, not embedded directly in Makefile syntax.

\---

**## Chapter 3 — Security Hardening**

**### 3.1 Secrets Management**

\- No credentials — database passwords, Redis passwords, Stripe secret keys, Stripe webhook signing secrets, AWS access keys — may ever be committed to the repository, at any point in its history.

\- All secrets are injected via environment variables, sourced from gitignored \`.env\` files, with a \`.env.sample\` documenting every required variable name with placeholder values.

\- AWS credentials must never be long-lived static keys hardcoded in code, Lambda environment variables, or Docker images. Use IAM roles attached directly to compute resources so credentials are issued temporarily and automatically by AWS.

**### 3.2 Network Isolation**

\- The backend exposes no port to the host; only the reverse proxy is publicly reachable.

\- PostgreSQL and Redis are unreachable from outside the Docker network under any circumstance.

\- Any AWS compute placed in a VPC uses security groups scoped to exactly the ports and destinations required, denying all else by default.

\- No part of the application logic may rely on network position alone as a security boundary — any route that would be sensitive if exposed directly must enforce its own authentication or signature check in code, independent of whether the network happens to isolate it correctly.

**### 3.3 Input Validation and Injection Prevention**

\- All SQL touching user-supplied input uses parameterized queries exclusively, with no exceptions, including inside the booking transaction's raw SQL.

\- All incoming request bodies are validated through typed Pydantic models with explicit, constrained allowed values before reaching any business logic.

\- Any data read from an asynchronous message (e.g. an SQS message body) is treated as untrusted and re-validated before use, even if it originated from your own backend.

**### 3.4 Webhook and Payment Security**

\- The payment provider's webhook signature is verified against the raw, unparsed request body before any business logic executes. Requests failing verification are rejected immediately with \`400\`.

\- The webhook signing secret is distinct per environment and never reused across environments.

\- The webhook handler must be idempotent — a duplicate delivery of the same payment confirmation event must not create a duplicate booking or trigger a duplicate side effect. Processed event identifiers must be tracked and checked before acting on an event.

**### 3.5 Authentication and Authorization**

\- Endpoints that create or modify bookings require authenticated identity (JWT in an \`Authorization\` header). A user may only act on their own bookings, enforced by server-side ownership checks, never trusted from a client-supplied field alone.

\- Any remaining internal-only routes are protected by a shared secret header distinct from user-facing authentication.

**### 3.6 Cloud Infrastructure Hardening**

\- Any object storage holding generated documents must not be publicly readable. Access is granted only via short-lived, signed URLs with a defined expiration.

\- Any message queue is restricted via IAM access policy to only the specific roles that need to publish or consume — no unrestricted access principals.

\- Any serverless compute follows least privilege: it can access only the specific resources its task requires, nothing broader.

\- Any dead-letter or failure queue receives the same access restrictions as the primary queue, with a bounded retention period rather than indefinite storage.

\- Any outbound email sending identity is domain-authenticated (SPF/DKIM) to prevent spoofing and avoid delivery to spam.

\- Logs must never contain full sensitive payloads, generated documents, or personal data in plaintext — log identifiers, not contents.

**### 3.7 Rate Limiting and Abuse Prevention**

\- The reverse proxy applies rate limiting on public endpoints, particularly checkout and webhook routes, before requests reach the backend.

\- You must be able to explain what is lost if the backend port were ever accidentally exposed directly — specifically that nginx's rate limiting and filtering would no longer apply to traffic bypassing it, and that any route relying implicitly on network isolation rather than its own authentication becomes exploitable the moment that isolation is bypassed.

**### 3.8 Defense in Depth**

Security here is layered, not singular:

\| Layer | What it protects against |

\|---|---|

\| Network isolation (nginx + private backend) | Unauthorized direct reach to backend |

\| Parameterized queries | SQL injection |

\| Pydantic validation | Malformed or unexpected input |

\| Webhook signature verification | Forged payment confirmations |

\| Least-privilege IAM roles | Blast radius of a compromised component |

\| Signed URLs | Unauthorized access to stored documents |

\| Rate limiting | Flooding, brute-force, abuse |

No single layer is assumed sufficient on its own.

\---

**## Chapter 4 — General Rules**

\- A single \`make up\` (wrapping \`docker-compose up --build\`) at the repo root must launch nginx, the FastAPI backend, PostgreSQL, Redis, and the React frontend.

\- The backend must handle errors gracefully — a failed transaction must never crash the container or leave a rogue lock.

\- No ORM may abstract the core booking transaction. You must write raw SQL for \`BEGIN\`, \`COMMIT\`, and \`ROLLBACK\`, executed through an async Postgres driver (\`asyncpg\`), to prove direct understanding of ACID principles.

\- An ORM may still be used for non-critical CRUD outside the booking transaction if desired — the raw-SQL constraint applies specifically to the booking lock/confirm path.

\- Every SQL query touching user-supplied input uses parameterized placeholders (\`$1\`, \`$2\`, ...). Never construct SQL via string concatenation or f-strings containing user input.

\---

**## Chapter 5 — Search & Availability**

**### 5.1 Schema**

Design the following tables in PostgreSQL:

\- **\*\*Users\*\*** — identity, authentication credentials (hashed passwords, never plaintext)

\- **\*\*Assets\*\*** — rentable items (rooms, vehicles, equipment, etc.)

\- **\*\*Bookings\*\*** — links a user to an asset over a date range, with a status

The booking's date range is stored as a native \`daterange\` column, not two separate \`start\_date\`/\`end\_date\` columns, so overlap semantics are expressed at the type level.

A \`CHECK\` constraint enforces that every range is internally valid (\`lower(during) < upper(during)\`), rejecting backwards or zero-length ranges before they reach overlap logic.

The booking \`status\` field is constrained to a fixed, defined set of values:

\| Value | Meaning |

\|---|---|

\| \`pending\_payment\` | User has initiated checkout, payment not yet confirmed |

\| \`confirmed\` | Payment confirmed via webhook, booking is real |

\| \`cancelled\` | Payment failed or user cancelled |

\| \`expired\` | Checkout window elapsed without payment |

This constraint is enforced at two independent layers:

\- Application layer: a typed Pydantic \`Enum\`, so invalid values are rejected at the API boundary

\- Database layer: a \`CHECK\` constraint or native Postgres \`ENUM\` type, so no code path — raw SQL, migration, manual query — can ever insert an invalid status

**### 5.2 The Overlap Query**

\- \`GET /api/assets/{id}/availability?start=&end=\` — a fast, read-only query with no locking involved, used for browsing and searching. This endpoint is called frequently and must remain cheap.

\- The overlap check uses the native range overlap operator (\`&&\`), never manual \`<=\`/\`>=\` comparisons.

\- A composite GiST index is created on \`(asset\_id, during)\`, narrowing the search to a single asset's bookings before the range-overlap tree search runs within that subset.

\- Target: fast resolution against a seeded dataset of 100k+ rows, well under 50ms.

\- The seed script used to generate this dataset is callable via \`make seed\`.

**### 5.3 Justification Requirement**

You must be able to explain:

\- Why a standard B-tree index cannot efficiently answer "which existing ranges overlap this new range"

\- How a GiST index organizes ranges into a tree of nested bounding regions, allowing entire irrelevant branches to be eliminated in one comparison rather than scanning row by row

\- Why \`[start, end)\` notation (inclusive start, exclusive end) is the correct convention for back-to-back bookings without wasted gap days

\---

**## Chapter 6 — Distributed Concurrency Control**

**### 6.1 The Lock Mechanism**

When a user initiates checkout for a specific asset and date range:

\- Attempt an atomic, time-limited lock in Redis using \`SET NX EX 60\` — "create this key only if it does not already exist, auto-delete after 60 seconds"

\- The key is named by asset identifier (e.g. \`booking\_lock:304\`) — a string your application defines, meaningless to Redis itself, meaningful to your own logic

\- If the lock is acquired: proceed to the payment step

\- If the lock is not acquired (someone else holds it): return \`409 Conflict\` immediately — the second user never reaches a payment form

**### 6.2 Redis for Cache and Lock Together**

Redis serves two independent purposes in this project, using the same single container:

\| Key pattern | Purpose |

\|---|---|

\| \`booking\_lock:{asset\_id}\` | Checkout lock (NX + EX, auto-expiring) |

\| \`cache\:availability:{asset\_id}\` | Cached availability results (read performance) |

These coexist in the same Redis instance without conflict. The naming convention is chosen by your application; Redis treats all keys identically regardless of naming.

**### 6.3 What the Lock Does and Does Not Do**

\- The lock does **\*\*not\*\*** prevent double-booking — that is solved at the transaction level in Chapter 7 by \`FOR UPDATE\` row locking

\- The lock **\*\*does\*\*** prevent a second user from being sent to a payment form for an asset that is actively being checked out, before any database transaction has run

\- The lock's expiration (\`EX 60\`) exists purely to reclaim abandoned checkout attempts — if a user closes their tab or loses connection, the key disappears after 60 seconds and the asset becomes available for new checkout attempts, with no manual cleanup required

\- Redis auto-expiration is a property of the storage engine itself — it requires no application-side cleanup loop, cron job, or scheduled task; the key simply ceases to exist when its timer ends

**### 6.4 Cleaning Up Stale Pending Rows**

When a new lock is successfully acquired, your application checks for and marks as \`expired\` any existing \`pending\_payment\` row for the same asset whose creation timestamp is older than the lock window. This is a single filtered \`UPDATE\` statement executed at the moment it is relevant, not a background process.

\---

**## Chapter 7 — The Booking Transaction**

This is the core of the project.

**### 7.1 The Transaction Sequence**

On a booking attempt, after the Redis lock is acquired:

\`\`\`

BEGIN;

SELECT \* FROM bookings

WHERE asset\_id = $1

AND during && daterange($2, $3)

FOR UPDATE;

\-- if no conflicting rows returned:

INSERT INTO bookings (asset\_id, during, user\_id, status)

VALUES ($1, daterange($2, $3), $4, 'pending\_payment');

COMMIT;

\`\`\`

**### 7.2 Requirements**

\- \`FOR UPDATE\` row-level locking is mandatory on the overlap check — this forces any other concurrent transaction for the same asset and overlapping range to block and wait rather than reading stale data and racing ahead

\- The transaction is atomic — the booking insert and any related counter updates either all succeed or all roll back together

\- On any failure inside the transaction, it explicitly rolls back and releases any associated Redis lock so the asset does not remain frozen

\- All values (\`asset\_id\`, \`start\`, \`end\`, \`user\_id\`) are passed as parameterized placeholders, never string-interpolated

**### 7.3 ACID Breakdown**

You must be prepared to explain each property's role in this specific transaction:

\| Property | What it does here |

\|---|---|

\| **\*\*Atomicity\*\*** | The INSERT and any counter UPDATE either both commit or both roll back — no partial state |

\| **\*\*Consistency\*\*** | CHECK constraints (valid range, valid status) are enforced — the database refuses any row violating declared rules |

\| **\*\*Isolation\*\*** | \`FOR UPDATE\` prevents two concurrent transactions from both reading "no conflict" and both inserting — one blocks until the other commits |

\| **\*\*Durability\*\*** | Once \`COMMIT\` returns, the booking survives any subsequent crash — written to the WAL before the commit returns |

\---

**## Chapter 8 — Transactional Integrity & Payment Webhooks**

You are strictly forbidden from trusting client-side signals for payment confirmation. The frontend reporting "payment succeeded" is not sufficient — it must be independently confirmed by the payment provider.

**### 8.1 Payment Flow**

\`\`\`

User clicks "Pay"

   │

   ▼

FastAPI creates PaymentIntent server-side → returns client\_secret to frontend

   │

   ▼

Frontend passes client\_secret to Stripe Elements → user enters card details

   │

   ▼

Stripe processes payment independently

   │

   ▼

Stripe calls POST /api/webhooks/stripe (arrives via nginx, forwarded untouched)

   │

   ▼

FastAPI verifies signature → runs confirmation transaction

\`\`\`

**### 8.2 Requirements**

\- Integrate Stripe in Test Mode

\- Generate a \`PaymentIntent\` server-side after the booking lock succeeds; pass only the client secret to the frontend — never the secret key

\- The webhook receiver lives in its own module (\`app/routers/webhooks.py\`), separated from booking routes

\- The handler reads the **\*\*raw, unparsed request body\*\*** and verifies Stripe's signature before doing anything else — per Chapter 3.4

\- Only on a verified \`payment\_intent.succeeded\` event does the backend execute the confirmation transaction: lock the booking row with \`FOR UPDATE\`, update status to \`confirmed\`, update related counters, all within one atomic transaction

\- On success: delete the Redis lock immediately

\- On failure: roll back the transaction and delete the Redis lock to avoid a frozen asset

\- Idempotency: store processed Stripe event IDs; if the same event ID arrives twice, skip it — per Chapter 3.4

**### 8.3 Stripe Event to Booking Status Mapping**

The translation between Stripe's event vocabulary and your booking status vocabulary is explicit, written once, and never passed raw through Pydantic:

\| Stripe event type | Your booking status |

\|---|---|

\| \`payment\_intent.succeeded\` | \`confirmed\` |

\| \`payment\_intent.payment\_failed\` | \`cancelled\` |

\| \`payment\_intent.canceled\` | \`cancelled\` |

\| Any other event type | Ignored — return 200, take no action |

\---

**## Chapter 9 — Client Interface**

\- A dashboard displaying assets with live state: Available, Locked, or Booked

\- A polling mechanism (interval refetch) reflecting state changes without requiring a manual refresh

\- A search/browse flow hitting the read-only availability endpoint, with no locking involved

\- A checkout flow using Stripe Elements, calling the backend only through the reverse proxy — never directly

\---

**## Chapter 10 — Testing**

Write automated tests after each module is functionally complete, covering the cases manually verified during development. Strict test-first methodology is not required.

**### 10.1 Non-Negotiable: The Concurrency Test**

Fire at least 50 simultaneous booking requests at the same asset and overlapping date range. Assert that exactly one succeeds and the rest return a clean \`409\` conflict response.

This test is runnable via \`make concurrency-test\`. It must exist and pass before the booking feature is considered complete — it is the only way to verify the race condition is genuinely prevented, since manual testing cannot reliably reproduce it.

**### 10.2 Webhook Tests**

\- A valid Stripe signature is accepted and processed

\- A tampered or missing signature returns \`400\` and takes no action

\- Delivering the same event ID twice does not produce a duplicate confirmed booking

**### 10.3 Data Integrity Tests**

\- A date range with end before start is rejected by the CHECK constraint

\- An undefined status value is rejected by the database constraint

\- The availability endpoint correctly returns unavailable for a confirmed booking overlapping the queried range

\- The availability endpoint correctly returns available for a non-overlapping range on the same asset

\---

**## Chapter 11 — CI/CD**

\- An automated workflow triggers on every push and pull request

\- The pipeline spins up PostgreSQL and Redis as service containers, runs linting, and runs the full test suite including the concurrency test

\- On success, the backend Docker image is built and tagged with the commit SHA

\- A failing test blocks merging

\---

**## Chapter 12 — Makefile Reference**

The repository root must contain a Makefile with at minimum the following targets:

\| Target | What it does |

\|---|---|

\| \`make build\` | Build all Docker images |

\| \`make up\` | Start all containers in detached mode |

\| \`make down\` | Stop and remove all containers |

\| \`make logs\` | Follow backend container logs |

\| \`make test\` | Run the full test suite |

\| \`make concurrency-test\` | Run only the 50-request concurrency test |

\| \`make seed\` | Seed the database with 100k+ rows for benchmarking |

\| \`make clean\` | Stop containers and remove volumes |

\| \`make restart\` | \`down\` then \`up\` |

Any target requiring real logic (health-check waiting, environment validation, seeding) delegates to a script under \`scripts/\`, called from the Makefile target.

\---

**## Chapter 13 — Bonus: Event-Driven Serverless Pipeline**

If the mandatory parts are not fully production-ready, the bonus is not evaluated.

**### 13.1 Pipeline Architecture**

\`\`\`

[Postgres COMMIT — booking confirmed]

              │

              ▼

    [Publish event to AWS SQS] ──► [Instant 200 OK to client]

              │

              ▼

       [AWS SQS Queue]

              │

              ▼

      [AWS Lambda function]

              │

       ┌──────┴──────┐

       ▼             ▼

[Generate PDF]  [Call AWS SES]

       │             │

       ▼             ▼

[Store in S3]  [Email signed URL to customer]

\`\`\`

**### 13.2 Requirements**

\- Immediately after the confirmation transaction commits, the backend publishes a lightweight event (\`booking\_id\`, \`user\_email\`) to an AWS SQS Standard Queue

\- The backend returns \`200 OK\` to the client instantly — it never blocks on PDF generation or email dispatch

\- An independent Python Lambda function triggers automatically on new queue messages: queries the booking record, generates a structured PDF receipt, stores it in S3, and emails a short-lived signed URL via SES

\- A Dead Letter Queue (DLQ) catches messages that fail repeatedly, preventing silent loss of the notification

\- All cloud infrastructure follows Chapter 3.6: least-privilege IAM roles, private S3 bucket, bounded DLQ retention, domain-authenticated sending identity

\---

**## Chapter 14 — Submission and Evaluation**

Submit inside your designated Git repository. The \`docker-compose.yml\`, Makefile, and all scripts must be clearly documented at the repository root. A README must explain every available \`make\` command and the project's architecture at a high level.

**### Defense Requirements**

During your defense, you must be prepared to explain:

**\*\*Architecture\*\***

\- Why the backend has no published port, and what is specifically lost if it were accidentally exposed

\- Why the reverse proxy's role is distinct from the backend's own request validation

**\*\*Database and Concurrency\*\***

\- Why the booking transaction uses raw SQL with explicit row-level locking instead of an ORM

\- What \`FOR UPDATE\` actually does at the database level and why removing it reintroduces the race condition

\- Why the date range uses a native range type with a GiST index rather than two plain columns with a B-tree index

\- What performance difference this produces at scale, and why the B-tree structure cannot efficiently answer an overlap query

**\*\*Payments and Webhooks\*\***

\- Why payment confirmation is driven by a verified webhook rather than a client-side report of success

\- How idempotency is implemented and what double-delivery would cause without it

**\*\*Security\*\***

\- What each layer of the security posture protects against

\- Why no single layer alone would be sufficient

**\*\*ACID\*\***

\- Which ACID property prevents the double-booking race condition (Isolation, via \`FOR UPDATE\`)

\- Which ACID property prevents partial writes from corrupting your data (Atomicity)

\- The distinction between these two, and why each exists independently

**\*\*Redis\*\***

\- The precise difference between the Redis lock and the Postgres \`FOR UPDATE\` lock — what each one prevents, and why both are needed

\- What \`SET NX EX 60\` does at the Redis level, including why atomicity of the NX check matters

\- Why Redis's key expiration is structurally different from implementing an \`expires\_at\` column in Postgres

\---

**## Additional Project — "Chat-with-your-Data" Dashboard (RAG)**

**What it is:** An integrated Retrieval-Augmented Generation (RAG) feature that lets authenticated users upload supported documents (initially PDFs and CSVs) and ask questions about their own data. The system retrieves relevant document chunks from a vector database and passes only the retrieved context to the LLM to generate an answer.

**Why it hooks recruiters:** Retrieval-Augmented Generation is a common enterprise use case for LLMs. Showing that you can extract and chunk documents, generate embeddings locally, store and retrieve vectors, enforce user-scoped access, and ground LLM responses in retrieved context demonstrates practical AI/backend engineering skills without depending on a paid embedding provider.

**Implementation constraints for this project:**

- This RAG feature is an additional project integrated into the existing rental platform. Do not create a separate standalone frontend application.
- The implementation must reuse the existing FastAPI backend and React/Vite frontend.
- The implementation must reuse the existing PostgreSQL database and authentication system where appropriate.
- The RAG implementation must be developed incrementally and must not replace or break the existing booking, payment, security, or concurrency requirements.
- The implementation must avoid unnecessary paid services. The embedding pipeline must run locally inside the FastAPI Docker container.
- Do not use OpenAI embeddings and do not require an OpenAI API key for embeddings.

**### Tech Stack**

- **RAG Service:** Python/FastAPI — implemented as routes/modules inside the existing FastAPI backend.
- **Frontend:** Existing React/Vite frontend. Add the chat-with-your-data UI as views/components inside the current frontend; no separate frontend application.
- **Vector Database:** ChromaDB `1.5.9`, self-hosted inside Docker and connected to FastAPI through the existing Docker network.
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`, executed locally with Sentence Transformers. The model produces 384-dimensional embeddings.
- **ML Runtime:** CPU-only PyTorch. CUDA/NVIDIA PyTorch dependencies are not required for the RAG embedding pipeline.
- **LLM / Generation:** Google Gemini `3.6 Flash`, accessed through the existing `google-genai` Python SDK and `GEMINI_API_KEY`. The model name must be configurable through `GEMINI_MODEL` and must not be hardcoded throughout the application.
- **Orchestration:** LangChain may be used for document splitting, retrieval, and prompt assembly where it provides clear value. Do not introduce unnecessary abstractions merely to use LangChain.
- **PDF extraction:** PyMuPDF.
- **CSV processing:** pandas.
- **Relational DB:** Existing PostgreSQL database. Store document metadata, ownership information, processing status, and source/chunk metadata when required. Do not create a second PostgreSQL instance.
- **File storage:** For the initial showcase implementation, uploaded source files may be stored using a clearly defined local/persistent storage mechanism appropriate to the existing Docker setup. Do not store raw document contents inside Chroma. If object storage is later introduced, use S3-compatible storage and signed URLs.
- **Auth:** Reuse the existing application's JWT authentication. Every document and chat operation must be scoped to the authenticated user. Do not create a second authentication system.

**### Docker and Persistence Requirements**

The RAG stack must run as part of the existing Docker Compose environment.

The existing Compose network contains the FastAPI service and a dedicated ChromaDB service:

```text
FastAPI API
    |
    | HTTP over rental_net
    v
ChromaDB
    |
    v
chroma_data Docker volume
```

The ChromaDB service uses:

```yaml
chroma:
  image: chromadb/chroma:1.5.9
  volumes:
    - chroma_data:/data
  networks:
    - rental_net
  restart: unless-stopped
```

The FastAPI service uses a persistent Hugging Face cache:

```yaml
api:
  volumes:
    - ./backend:/app
    - huggingface_cache:/root/.cache/huggingface
```

The root Compose volumes include:

```yaml
volumes:
  postgres_data:
  chroma_data:
  huggingface_cache:
```

The `huggingface_cache` volume exists so that downloaded Sentence Transformer model files survive API container recreation and do not need to be downloaded again unnecessarily.

The RAG implementation must not expose ChromaDB directly to the public host unless there is a documented development/debugging reason. FastAPI communicates with Chroma using the Docker service hostname:

```text
http://chroma:8000
```

The existing reverse-proxy/network-isolation requirements remain in force.

**### RAG Pipeline**

The mandatory pipeline is:

```text
User uploads document
        |
        v
FastAPI validates authenticated user + file
        |
        v
PDF/CSV text extraction
        |
        v
Document chunking
        |
        v
all-MiniLM-L6-v2
(local CPU embedding)
        |
        v
384-dimensional vectors
        |
        v
ChromaDB
        |
        | similarity search
        v
Relevant document chunks
        |
        +---- user question
        |
        v
Gemini 3.6 Flash
        |
        v
Grounded answer
```

The implementation must keep retrieval and generation conceptually separate:

1. **Retrieval:** convert the user question into a local embedding and retrieve relevant chunks from ChromaDB.
2. **Generation:** provide the retrieved chunks plus the user's question to Gemini 3.6 Flash and instruct the model to answer using the supplied context.

The LLM must not be asked to answer from arbitrary unsupported knowledge when the requested information is expected to exist in the user's uploaded data.

**### Embedding Requirements**

Use exactly:

```text
sentence-transformers/all-MiniLM-L6-v2
```

for the initial implementation.

The embedding model must be loaded locally by the FastAPI application and reused rather than instantiated for every request.

Expected embedding dimension:

```text
384
```

The project has already verified the embedding pipeline successfully:

```text
PyTorch: CPU-only
CUDA available: False
Embedding shape: (384,)
```

Do not replace this model with `text-embedding-3-small`, `text-embedding-3-large`, or another paid embedding API.

The Hugging Face model cache must be persisted through the Docker `huggingface_cache` volume.

A Hugging Face authentication token is not required for this public model in the initial implementation. Do not introduce `HF_TOKEN` as a mandatory environment variable unless rate limits later make it necessary.

**### ChromaDB Requirements**

Use ChromaDB as the vector store.

FastAPI must connect to the Chroma service using the Docker hostname:

```python
chromadb.HttpClient(host="chroma", port=8000)
```

The vector database must persist data through the `chroma_data` Docker volume.

Each stored chunk must retain enough metadata to identify:

- the authenticated owner/user
- the source document
- the document/chunk identifier
- page number or source row where applicable
- any other metadata needed to return useful citations/source information

Do not put entire raw uploaded files into Chroma. Chroma stores embeddings, document chunks, and metadata needed for retrieval.

Retrieval must enforce user ownership. A user must never retrieve chunks belonging to another user.

The implementation must include at least one similarity-search test proving that a semantically relevant chunk is returned for a natural-language question.

**### Document Ingestion**

The initial mandatory formats are:

- PDF
- CSV

For PDFs, use PyMuPDF to extract text while retaining page information where practical.

For CSVs, use pandas and convert rows/records into searchable textual representations while preserving source-row metadata.

Documents must be split into meaningful chunks before embedding. Chunk size and overlap must be configurable rather than scattered as magic numbers throughout the code.

The ingestion process should:

1. validate the authenticated user;
2. validate the file type and size;
3. create/store document metadata;
4. extract text;
5. split the extracted content into chunks;
6. generate local embeddings;
7. store chunks + embeddings + metadata in Chroma;
8. mark processing as successful only after the vector data has been stored successfully.

Failures must be handled cleanly without leaving misleading "completed" document state.

**### Retrieval**

A chat/question endpoint must:

1. authenticate the user;
2. convert the question into a local 384-dimensional embedding;
3. query ChromaDB for the most relevant chunks belonging to that user;
4. reject or gracefully handle empty/no relevant context;
5. assemble a bounded prompt containing the question and retrieved context;
6. send the prompt to Gemini 3.6 Flash;
7. return the generated answer together with useful source/document references where available.

The number of retrieved chunks must be configurable.

Do not blindly send an unlimited number of chunks to Gemini. Retrieved context must be bounded to control latency, prompt size, and cost.

**### Gemini Requirements**

Use the existing Google GenAI SDK:

```text
google-genai
```

The API key must come from:

```text
GEMINI_API_KEY
```

The model must come from:

```text
GEMINI_MODEL
```

with the configured project value:

```text
gemini-3.6-flash
```

Do not hardcode the API key.

Do not expose the Gemini API key to the React frontend.

The frontend communicates only with the FastAPI backend. FastAPI performs the Gemini API call server-side.

The generation prompt must clearly distinguish trusted retrieved context from the user's question and should instruct Gemini to avoid inventing facts that are not supported by the retrieved context.

**### Source Grounding**

The RAG response should identify the source documents/chunks used to construct the answer when practical.

If the retrieved context does not contain enough information to answer the question, the system should say that the information was not found in the user's uploaded data rather than confidently fabricating an answer.

This behavior is important for the showcase: the project should demonstrate that the answer is grounded in retrieved user data rather than being a generic chatbot.

**### API / Frontend Integration**

The RAG functionality should be exposed through authenticated FastAPI routes.

At minimum, the implementation should provide functionality equivalent to:

- upload/index a document;
- inspect the authenticated user's documents and processing state;
- ask a question against the authenticated user's indexed data.

Exact route names may follow the existing project's router conventions.

The React frontend should provide:

- a document upload interface;
- a list/status view for uploaded documents;
- a chat/question interface;
- displayed answers;
- source references when returned by the backend;
- useful loading/error states.

The RAG UI must be integrated into the existing application rather than creating a second frontend.

**### Testing Requirements**

Tests must be added incrementally after each RAG component becomes functional. Strict test-first development is not required.

At minimum, test:

- the embedding model produces a 384-dimensional vector;
- ChromaDB is reachable from the API container;
- a document can be chunked and indexed;
- a semantic query retrieves the expected relevant chunk;
- document ownership prevents one user from retrieving another user's chunks;
- PDF extraction preserves useful source/page information;
- CSV ingestion preserves useful row/source information;
- an empty or irrelevant retrieval is handled safely;
- Gemini is called server-side and the API key is never exposed to the frontend;
- the final response contains grounded context/source information when available;
- ingestion failures do not incorrectly mark documents as successfully processed.

A simple end-to-end RAG test should prove:

```text
document
  -> extraction
  -> chunking
  -> local embedding
  -> Chroma storage
  -> question embedding
  -> similarity retrieval
  -> Gemini generation
  -> grounded answer
```

The previously verified infrastructure test should remain reproducible:

```text
FastAPI -> ChromaDB heartbeat
```

and:

```text
all-MiniLM-L6-v2 -> (384,)
```

**### Dependency Requirements**

The backend RAG dependencies required by this specification are:

```text
chromadb
langchain
langchain-chroma
langchain-text-splitters
sentence-transformers
google-genai
PyMuPDF
pandas
```

Do not add `langchain-openai` or `openai` for embeddings.

If an existing dependency is already used elsewhere in the project, keep it only when it has a real purpose outside the replaced OpenAI embedding path.

PyTorch must be installed as a CPU-only build so the Docker image does not pull unnecessary NVIDIA/CUDA runtime packages.

**### Cost / Showcase Constraint**

The RAG feature must be demonstrable without paying for OpenAI embeddings or a hosted vector database.

The intended showcase architecture is:

```text
                 LOCAL / DOCKER
                 --------------
PDF / CSV
   |
   v
PyMuPDF / pandas
   |
   v
Sentence Transformers
all-MiniLM-L6-v2
   |
   v
384-dim vectors
   |
   v
ChromaDB
   |
   | retrieved context
   v
Gemini 3.6 Flash
   |
   v
Answer + sources
```

The only external AI service in the initial RAG implementation is Gemini for generation. Embeddings and vector storage remain local/self-hosted.

**### Implementation Discipline**

Do not blindly add packages, rewrite working infrastructure, or rebuild the entire architecture for every RAG component.

Implement and verify incrementally:

```text
dependency
    ->
Docker build
    ->
component test
    ->
integration test
    ->
next component
```

The already verified components are considered working:

- CPU-only PyTorch
- `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional local embeddings
- ChromaDB `1.5.9`
- FastAPI-to-Chroma Docker networking
- persistent Docker volumes for Chroma and Hugging Face cache

Future changes must preserve these working components unless a concrete technical problem is demonstrated.

---

