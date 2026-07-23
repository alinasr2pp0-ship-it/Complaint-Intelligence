# خطة الاختبار — Consumer Complaints RAG Chatbot

This document is a production-ready testing roadmap, directly linked to the actual test suite in backend/tests/. Each testing stage references its corresponding test file, the number of test cases, and the execution command.


## الحالة الحالية

```
88 passed, 8 skipped in ~3s     (pytest, بدون أي مفتاح API حقيقي أو اتصال إنترنت)
```

الـ 8 اللي بيتخطوا هما تحديدًا الاختبارات اللي بتكلّف فلوس فعلية أو محتاجة
index حقيقي على Pinecone — مش فاشلة، مُتخطّاة عن قصد (تفاصيل تحت في القسم
الأخير).

---

## بنية الاختبارات

```
                              Tests
                                │
        ┌───────────────┬───────────────┬───────────────┐
        │               │               │               │
   Unit Tests      Integration      End-to-End      Performance
   (مجانية،        (خدمة واحدة      (المسار كامل:    (زمن استجابة،
    مُموَّهة،         حقيقية،          المستخدم ←        throughput)
    < 3 ثواني)       اختياري)         API ← Pinecone
                                       ← OpenRouter)
        └───────────────┴───────────────┴───────────────┘
                                │
                        Evaluation Tests
                    (ROUGE / BLEU / Recall@K / MRR)
                                │
                       Optimization Tests
                         (A/B Testing)
```

**المبدأ الأساسي:** أي اختبار بيتكلم مع Pinecone / Voyage / OpenRouter
فعليًا اتحط في تصنيف منفصل (`manual` أو `e2e`) ومتخطّى تلقائيًا من التشغيل
الافتراضي. الاختبارات الافتراضية (`unit`) كلها بتستخدم mocks — بتتأكد من
منطق الكود نفسه، مش من توفر أو تسعير أي خدمة خارجية.

---

## المرحلة 1 — Configuration Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/config/settings.py` |
| **ملف الاختبار** | `tests/test_config.py` — 7 اختبارات |
| **بماذا نختبر** | قراءة `OPENROUTER_API_KEY` / `VOYAGE_API_KEY` / `PINECONE_API_KEY` من env، سلوك الـ defaults، ترتيب سلسلة OpenRouter، تحويل `CORS_ORIGINS`، حساب `DATA_CSV_PATH` من مكان الملف (لا hardcoded) |
| **لماذا** | المشروع بالكامل يعتمد على هذه الإعدادات — إذا فشل هذا الجزء، لا شيء آخر يعمل |
| **التشغيل** | `pytest tests/test_config.py -v` |

## المرحلة 2 — Logger Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/core/logging_config.py` |
| **ملف الاختبار** | `tests/test_logging.py` — 5 اختبارات |
| **بماذا نختبر** | ضبط الـ level من `LOG_LEVEL`، fallback عند قيمة غير صحيحة، فعلاً بتتطبع الرسائل، تهدئة المكتبات الخارجية الصاخبة (httpx, pinecone...) |
| **لماذا** | لتتبع الأخطاء أثناء التشغيل — لو الـ logging نفسه معطوب، أي مشكلة إنتاج تبقى عمياء |
| **التشغيل** | `pytest tests/test_logging.py -v` |

## المرحلة 3 — Exception Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/core/exceptions.py` |
| **ملف الاختبار** | `tests/test_exceptions.py` — 8 اختبارات |
| **بماذا نختبر** | `ConfigurationError → 500`, `VectorStoreNotReadyError → 503`, `GenerationError → 502`، وإن الـ unhandled-exception handler بيخفي تفاصيل الخطأ الداخلية عن الـ client |
| **لماذا** | حتى لا ينهار الـ API، ولا يسرّب تفاصيل داخلية حساسة في رسالة الخطأ |
| **التشغيل** | `pytest tests/test_exceptions.py -v` |

## المرحلة 4 — API Endpoint Tests

| | |
|---|---|
| **الملفات المُختبَرة** | `app/api/chat.py`, `retrieval.py`, `health.py` |
| **ملف الاختبار** | `tests/test_api_endpoints.py` — 11 اختبار (عبر `TestClient` حقيقي لتطبيق FastAPI) |
| **بماذا نختبر** | `POST /chat` بـ JSON صحيح يرجع `ChatResponse`، `question=""` يرجع `422`، JSON مشوّه يرجع `422`، تمرير `k` كـ query param، نفس الشيء لـ `/retrieve` |
| **لماذا** | هذا العقد الفعلي (contract) اللي الفرونت إند معتمد عليه — أي كسر هنا بيوصل للمستخدم مباشرة |
| **التشغيل** | `pytest tests/test_api_endpoints.py -v` |

## المرحلة 5 — Schema Tests

| | |
|---|---|
| **الملفات المُختبَرة** | `app/schemas/*.py` |
| **ملف الاختبار** | `tests/test_schemas.py` — 10 اختبارات |
| **بماذا نختبر** | `ChatRequest(question="")` يُمنع، `question=None` يفشل، حدود `k` (1-20) في `RetrievalRequest`، القيم الافتراضية لـ `sources` |
| **لماذا** | لمنع البيانات الخاطئة من دخول النظام أصلًا |
| **التشغيل** | `pytest tests/test_schemas.py -v` |

## المرحلة 6 — Data Loader Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/utils/data_loader.py` |
| **ملف الاختبار** | `tests/test_data_loader.py` — 7 اختبارات |
| **بماذا نختبر** | تحويل كل صف CSV لـ `Document`، إسقاط الصفوف بدون `rag_document`، صحة الـ metadata (`complaint_id`, `company`)، احترام `max_rows` |
| **لماذا** | الـ Retriever يعتمد بالكامل على صحة هذه البيانات وقت البناء |
| **التشغيل** | `pytest tests/test_data_loader.py -v` |

## المرحلة 7 — Vector Store Builder Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/vector_store/builder.py` |
| **ملف الاختبار** | `tests/test_vector_store_builder.py` — 6 اختبارات (Pinecone و Voyage مُموَّهين بالكامل) |
| **بماذا نختبر** | `ensure_index_exists()` بينشئ الـ index لو مش موجود ويتخطاه لو موجود، عدد الـ vectors المرفوعة = عدد الـ documents عبر كل الـ batches، الـ IDs المستخدمة = `complaint_id` (deterministic) |
| **لماذا** | لو البيانات ما اترفعتش صح، الـ Retriever مش هيلاقي أي نتائج — والـ IDs الثابتة هي اللي بتمنع التكرار عند إعادة التشغيل |
| **التشغيل** | `pytest tests/test_vector_store_builder.py -v` |

## المرحلة 8 — Vector Store / Retriever Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/vector_store/store.py` |
| **ملف الاختبار** | `tests/test_vector_store.py` — 10 اختبارات |
| **بماذا نختبر** | الاتصال بـ Pinecone، إيجاد الـ namespace، بناء الـ retriever بالـ defaults الصحيحة (`k=3`, `similarity`)، `vector_store_is_ready()` بيرجع `False` بأمان عند أي خطأ اتصال (مش بيرمي exception) |
| **لماذا** | هذا الكود بيتنفذ في كل request — لو `is_ready()` كذبت، المستخدم بياخد رسالة غامضة بدل "الخدمة لسه بتتجهز" |
| **التشغيل** | `pytest tests/test_vector_store.py -v` |

## المرحلة 9 — Prompt Construction Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/rag/prompts.py` |
| **ملف الاختبار** | `tests/test_prompts.py` — 7 اختبارات |
| **بماذا نختبر** | دمج الـ `Document`s في context واحد، وجود الـ context والسؤال في الـ prompt النهائي، الفرق بين `get_prompt` نسخة v1 وv2 |
| **لماذا** | prompt ناقص = استدعاء LLM مكلف فعليًا وبيرجع إجابة عشوائية |
| **التشغيل** | `pytest tests/test_prompts.py -v` |

## المرحلة 10 — LLM & Fallback Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/rag/chain.py` |
| **ملف الاختبار** | `tests/test_llm_fallback.py` — 6 اختبارات (يُسمى **Fallback Testing**) |
| **بماذا نختبر** | الموديل الأساسي بيتجرب الأول، عند فشله بينتقل للموديل التالي بالترتيب المحدد بالضبط، لو كل الموديلات فشلت بيرمي `GenerationError` واضح بدل انهيار غامض |
| **لماذا** | هذا أهم ضمان مرونة في المشروع — سلسلة OpenRouter المجانية بديل Gemini بالكامل، فلازم يتأكد إنها بتشتغل صح عند الفشل الجزئي |
| **التشغيل** | `pytest tests/test_llm_fallback.py -v` |

## المرحلة 11 — Chat Service Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/services/chat_service.py` |
| **ملف الاختبار** | `tests/test_chat_service.py` — 5 اختبارات |
| **المسار المُختبَر** | `Question → Retriever → Prompt → LLM → ChatResponse` |
| **بماذا نختبر** | الإجابة مش فاضية، الـ sources متطابقة مع الـ documents المسترجعة، قص الـ snippets الطويلة لـ 300 حرف |
| **لماذا** | ده القلب الوظيفي لـ `/chat` — أي خطأ هنا بيوصل مباشرة لتجربة المستخدم |
| **التشغيل** | `pytest tests/test_chat_service.py -v` |

## المرحلة 12 — Retrieval Service Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/services/retrieval_service.py` |
| **ملف الاختبار** | `tests/test_retrieval_service.py` — 5 اختبارات |
| **بماذا نختبر** | إرجاع أول `k` نتائج، صحة الـ metadata، التعامل الآمن مع metadata ناقصة |
| **لماذا** | `/retrieve` هو أداة تصحيح الأخطاء الأساسية لجودة البحث بدون تكلفة توليد |
| **التشغيل** | `pytest tests/test_retrieval_service.py -v` |

## المرحلة 13 — Health Check Tests

| | |
|---|---|
| **الملف المُختبَر** | `app/api/health.py` |
| **ملف الاختبار** | جزء من `tests/test_api_endpoints.py` — 2 اختبار |
| **بماذا نختبر** | `Pinecone متصل → vector_store_ready=true`، `غير متصل → false` (لكن الـ endpoint نفسه دايمًا بيرجع `200`) |
| **لماذا** | أسرع طريقة تتأكد بيها من حالة كل المفاتيح قبل ما تجرب أي endpoint تاني |
| **التشغيل** | `pytest tests/test_api_endpoints.py -k health -v` |

---

| المرحلة | الملف الأصلي | ماذا نقيس | لماذا |
|---|---|---|---|
| 14. Generation Evaluation | `generation_metrics.py` | ROUGE-1, ROUGE-L, BLEU, Latency لكل سؤال | قياس جودة الإجابات |
| 15. Retrieval Evaluation | `retrieval_metrics.py` | Recall@1/3/5, MRR | قياس جودة البحث |
| 16. Qualitative Evaluation | `run_qualitative.py` | مراجعة يدوية لـ 9 أسئلة ثابتة | بعض الأخطاء لا تظهر بالأرقام |
| 17. Optimization (A/B) | `prompt_comparison.py`, `embedding_comparison.py`, `chunk_comparison.py`, `strategy_comparison.py` | v1 مقابل v2، voyage-3 مقابل voyage-3-large، 300 مقابل 600، similarity مقابل mmr | اتخاذ قرار مبني على بيانات لا تخمين |
| 18. End-to-End Pipeline | كامل: `User → POST /chat → API → Service → Retriever → Pinecone → Prompt → OpenRouter → JSON` | نجاح المسار الكامل فعليًا | الاختبار الوحيد اللي بيثبت إن النظام شغّال من منظور المستخدم النهائي |
| 19. Performance & Stress | latency, throughput, memory, embedding time, retrieval time, generation time | حدود زمنية مقبولة | endpoint شغّال لكن بطيء = تجربة مستخدم سيئة برضو |

---