# Available project attachment text

These are the guideline/reference files explicitly referenced in retrieved project messages. Image-only attachments and inaccessible files cannot be reconstructed from chat text.


---

## C:\Users\ikari\.codex\attachments\090d5dd0-d1cc-4959-937a-085f9d8bb729\Pasted text.txt

Chapter 5: System Implementation, Testing and Evaluation
Note: As you read these notes, please refer to the shared sample documentations in your Google Classroom. 
5.1 Introduction
Chapter 5 explains how the approved design was implemented, made available in a suitable environment, tested and evaluated. It should show what was actually built, how the components work together, the evidence produced during implementation, and the extent to which the completed solution satisfies the objectives and requirements.
The organisation of this chapter will not be identical for every project. Select and number only the subsections that fit the project type, then agree on the final structure with the supervisor. The routes below cover general software and information systems, AI and machine learning, IoT and embedded systems, cybersecurity, blockchain and other specialised or hybrid projects. They are guides—not headings that every student must copy. Chapter 5 should finish with evaluated results, discussion and limitations; the final conclusions, recommendations and future works belong in Chapter 6.
📌 Writing Perspective and Evidence
Write mainly in the past tense because implementation and testing describe completed work. Use the present tense when explaining what the finished system, table or figure shows. Write in the third person and support claims with traceable evidence such as configuration records, repository history, test results, logs, measurements, figures and supervisor-verified demonstrations. Screenshots may support the discussion, but screenshots alone are not proof that a requirement was met.
5.2 Implementation Environment
The implementation environment describes where the solution was developed, tested and deployed, together with the hardware, software, services and configuration required to reproduce or use it. Distinguish the development environment from the test, staging, pilot or production environment. Do not state that a system is publicly available unless it has actually been deployed for public access; describe a local prototype, controlled pilot or private deployment accurately.
State the minimum configuration that was actually tested and justified. Avoid copying outdated platform examples or vendor marketing specifications. Versions, service tiers and hardware thresholds should come from the implemented solution, measurements, official documentation or controlled experiments.
5.2.1 Hardware and Deployment Environment
Describe the client devices, servers, cloud resources, storage, network connectivity and specialised hardware used by the project. Explain both the development or training equipment and the minimum environment required to run the finished solution. Where the project uses a managed cloud service, record the relevant service, region where material, instance or tier, storage, network assumptions and scaling limits without exposing credentials.
Use a compact table such as Table 5.1. Replace the guidance text with project-specific values and evidence. A stated minimum must be supported by a test, measurement, datasheet or provider configuration rather than guesswork.
Table 5.1: Implementation environment and minimum requirements
Item or layer
Minimum tested specification or version
Purpose and justification
Evidence or source
Client device
State processor, memory, storage, operating system and connectivity.
Explain the intended user tasks and the tested minimum.
Device test, measurement or official documentation.
Server or cloud runtime
State compute, memory, storage, service tier and network.
Explain workload, availability and scaling assumptions.
Deployment configuration and benchmark.
Specialised hardware
State the device, sensor, gateway, accelerator or peripheral.
Explain its role, interface and selection reason.
Datasheet, calibration record or experiment.


Additional Evidence for IoT and Embedded Projects
For an IoT or embedded project, identify each sensor, actuator, microcontroller, gateway, communication module, power component and external service that materially affects the solution. Explain its role, interface, operating range, calibration or accuracy where relevant, and why it was selected. Show the end-to-end chain from sensing or input, through local processing and communication, to the action, alert or stored record.
Use one clear, properly attributed image for each distinct component only where the image helps identification. A part number or model is often more useful than a decorative picture. Table 5.2 provides a suitable structure.
Table 5.2: IoT or embedded component evidence
Component
Image or model/part number
Role and connection
Key specification and justification
Sensor or input device
Insert one clear image or state the model/part number.
State the variable, unit, interface and connection.
State the range, accuracy, calibration and selection reason.
Actuator, controller or gateway
Insert one clear image or state the model/part number.
State the control, processing or communication role.
State the power, protocol or performance specification and selection reason.


5.2.2 Software, Services and Configuration
Identify the operating systems, runtimes, frameworks, libraries, databases, application servers, package managers, container tools, mobile platforms, cloud services and external APIs required to build and run the project. Record the exact versions or version ranges that were tested, their purpose, and the reason they were selected.
Discuss Docker, npm, Composer, Firebase, messaging services, email services or similar technologies only when they were genuinely used. Explain the configuration and role of each relevant dependency rather than listing product names. If containers are used, document the images, environment variables, volumes, ports and deployment differences; the Docker Compose production guidance is a useful starting point. Never expose passwords, API keys, tokens, private certificates or personal data in the report, screenshots or repository.
5.2.3 Deployment and Reproducibility
Provide a concise, reproducible account of how the solution is installed, configured, started and verified. Include the dependency or environment files, database migrations, seed or sample data where lawful, model or firmware version, build commands, deployment steps, and a simple health check or demonstration procedure. State any assumptions, paid services, licences, restricted datasets or network dependencies that another authorised person would need.
🧭 Select the Route That Fits the Project
General software and information systems — emphasise application modules, database implementation, interfaces, access control, integrations, deployment and user workflows.
AI and machine learning — emphasise dataset provenance, data preparation, experiment design, model training and selection, evaluation, model packaging, inference and monitoring.
IoT and embedded systems — emphasise component assembly, circuit and firmware implementation, protocols, calibration, power, connectivity, gateway or cloud integration and end-to-end operation.
Cybersecurity — emphasise the authorised test environment, assets and threats, control implementation, detection or protection logic, safe attack simulation, evidence handling and repeatable evaluation.
Blockchain or distributed systems — emphasise network choice, smart-contract or protocol implementation, identities and keys, transaction flow, deployment, cost, security and performance.
Other or hybrid projects — define an evidence path that matches the objectives, system boundary and evaluation plan, then confirm it with the supervisor.
5.3 System Implementation
Describe implementation in an order that matches the architecture, modules, data or experimental pipeline shown in Chapter 4. For each major component, link the relevant requirement and design, explain the chosen technology and implemented behaviour, show how it integrates with other components, and identify evidence that it works. Record material deviations from the approved design and justify them. Do not turn the chapter into a code listing; use short extracts only when they explain a non-obvious algorithm, interface, configuration or safety decision.
5.3.1 Implemented Modules, Integration and User Workflows
For a general software or information-system project, organise implementation around the modules and the user’s tasks. A suitable sequence is database implementation, application modules, integration and user workflows, followed by testing and discussion. Use headings that describe the actual system and adapt the numbering with your supervisor. The example below uses a maternal healthcare appointment and information portal; the wording is illustrative and should be replaced with evidence from the student’s implementation.
🗃️ Database and Data Implementation
Explain how the Chapter 4 data design was implemented: tables or collections, important fields, relationships, validation rules and access permissions. Identify any imported records or sample data and explain their preparation. Show a small, anonymised sample or relevant database extract, then explain how it supports a requirement.
✍️ Example: “The database stored user accounts, appointment slots and bookings. Each booking linked a user to an available slot and recorded its status. Validation prevented incomplete bookings, while access permissions restricted users to the records permitted by their role.” Adapt this paragraph to the actual schema and explain how duplicate or conflicting bookings were handled.
⚙️ Application Modules and Business Rules
Describe each major module’s purpose, inputs, processing and outputs, together with the technology used and the related requirement. For the maternal portal, these might include registration, appointment booking, approved information pages and staff administration. Explain how authentication, permissions and booking rules were implemented. Include short code extracts only where they clarify an important decision.
🔗 Integration and User Workflows
Follow one complete task through the interface, application logic and database. In the portal example, a user signs in, selects an available appointment, submits a booking and receives confirmation. Explain how the booking is stored and becomes visible to authorised staff. Where reminders or external services are used, describe the connection and what happens if delivery fails. Use numbered, captioned screenshots to show meaningful steps, including validation or error messages.
🧪 Testing and Results
Use the test-case format in Section 5.4.2 of these notes to compare expected and actual outcomes. For the portal, test successful booking, missing details, an unavailable slot, unauthorised access and cancellation. Add performance and recovery tests where required. For user acceptance or usability evaluation, report who participated, the tasks attempted and the findings. Discuss whether the evidence supports the objectives; a completed booking test does not by itself establish that users found the portal easy to use.
5.3.2 Data and Model Implementation for AI/ML Projects
For an ML project, organise the chapter around the data-to-model workflow. Elvis’s Chapter 5 illustrates this clearly: Dataset Description comes before Model Training and Evaluation, followed by Functional Testing and Results and Discussion. You may therefore use “5.3 Dataset Description” and “5.4 Model Training and Evaluation” in your own report, then renumber the remaining relevant sections. The headings in these class notes show alternative project routes; select and adapt them with your supervisor.
📊 Dataset Description
Introduce each dataset by name and source, explain why it suits the research objective, and describe what one record contains. Report the actual size, language, topic or class distribution, ownership or licence, inclusion and exclusion criteria, and any privacy restrictions. Explain the contribution of each source when combining datasets. Include a small, captioned sample and a summary of the final dataset; discuss what they show.
✍️ Maternal Healthcare Question Answering — illustrative wording: “The dataset comprised maternal healthcare questions paired with reference answers and their supporting source passages. Each record contained a question, reference answer, source identifier and topic label. The topic labels were used to examine coverage across antenatal, childbirth and postnatal questions.” Adapt this description to the actual records, cite the sources, and add the measured counts and languages. This example does not establish that a dataset has been collected or clinically reviewed.
🧹 Data Preparation and Partitioning
Explain how the raw data became usable model input: missing or duplicate records, corrections, exclusions, feature extraction or tokenisation, and the final training, validation and test split. State counts as well as proportions and justify the split. Keep related records together where needed to prevent leakage; fit learned preprocessing on training data only. Use augmentation or encoding only when appropriate to the task.
For the maternal QA example, describe how question–answer pairs were checked against their source passages, how incomplete records were handled, and how questions were formatted for the selected model. Keep duplicate questions and their paraphrases in the same partition. Explain any document-level grouping and whether evaluation tests new questions from known sources or questions from unseen sources. Show one permitted sample before and after preparation, with a short explanation of the change.
⚙️ Model Training and Selection
Introduce the baseline and candidate models, then explain their inputs, outputs and selection rationale. Record the model version, important hyperparameters, random seeds, training environment, stopping rule and saved artefacts. Justify cross-validation when used; the number of folds must suit the data. Select the final configuration using validation evidence and reserve the test set for final evaluation. Retain configuration files and experiment logs so the reported run can be reproduced.
For a fine-tuned maternal QA model, compare the original pretrained model with the fine-tuned version under the same evaluation conditions. Explain how questions and any supplied context become input and reference answers become training targets. Report the actual learning rate, batch size, epochs and token limits. If the project instead uses retrieval-augmented generation, describe passage preparation, indexing, retrieval and prompting; report model training only if it occurred.
🧪 Model Evaluation and Application Testing
Choose evaluation measures for the task. For maternal QA, explain the selected answer-quality measures and inspect examples of correct, incomplete and unsupported answers. Exact Match or token-level F1 may support comparison with reference answers where suitable, but text overlap alone does not establish clinical correctness. Describe any qualified domain review actually conducted, including the rubric and sample evaluated. Report measured results and limitations before drawing conclusions.
Then show how the selected model works in the application: a user submits a question, the system processes it, and an answer is displayed. Test valid, empty, out-of-scope and unsupported questions, response time, and the intended fallback or referral behaviour. Present expected and actual outcomes using the test-case format in Section 5.4.2 of these notes. In the discussion, connect model results and application tests to the research objectives. Use actual outputs; the example provides a writing sequence, not findings to copy.
5.3.3 Hardware, Firmware and Integration for IoT/Embedded Projects
For an IoT or embedded project, follow the physical-to-software sequence: component assembly, firmware and data acquisition, communication and integration, then testing and discussion. You may use “5.3 Hardware and Firmware Implementation” with these as subsections, adapting the remaining numbering to your project. The example below uses a maternal healthcare monitoring prototype. Describe the devices and behaviour actually implemented, and treat the example wording as illustrative.
🔌 Component Assembly and Connections
Build on the component table in Section 5.2 by explaining how the selected sensors, controller, gateway, power supply and any actuators were connected. State the relevant pins, interfaces and power requirements. Include a labelled photograph of the assembled prototype and relate it to the circuit or architecture in Chapter 4. Explain and justify any changes made during implementation.
✍️ Example: “The prototype connected the selected sensor to a microcontroller, which collected readings and forwarded them to a monitoring dashboard through a gateway. Each transmitted record contained a device identifier, timestamp, measured value and unit.” Replace the generic component names with the actual devices and explain the connections. Distinguish simulated inputs, bench measurements and any authorised participant measurements.
⚙️ Firmware and Data Acquisition
Explain how the firmware initialises the device, samples the sensor, checks readings and prepares records for transmission. State the sampling interval, units, calibration procedure and handling of missing or invalid readings. For the monitoring example, describe how a reading is compared with a reference instrument or controlled input and how measurement error is recorded. If alerts use thresholds, justify their source and show the implemented decision rule; a prototype threshold is not evidence of clinical validity.
📡 Communication and System Integration
Trace a reading from the device through the chosen protocol, gateway or server to storage and display. Explain message format, device authentication, buffering and retry behaviour where implemented. In the example, show how the dashboard associates a reading with the correct device, displays its timestamp and indicates stale data. Describe what happens when the sensor disconnects, the network fails or power is restored, including whether queued readings are recovered without duplication.
🧪 Component and End-to-End Testing
Test individual components before the complete workflow. For the monitoring prototype, present calibration error, reading-to-display delay, successful message delivery and recovery after disconnection, with the test conditions and repetitions. Evaluate power use or communication range where relevant to the requirements. Use Section 5.4.2’s test-case format for expected and actual behaviour, including alerts and failures. Retain circuit photographs, serial logs and message traces, and explain what each item demonstrates. Discuss the limits of the tested conditions and any remaining faults.
5.3.4 Cybersecurity, Blockchain and Other Specialised Projects
Cybersecurity projects should define the authorised laboratory or target scope, threat assumptions, datasets or traffic, control or detection implementation, tool configuration and safeguards used to prevent harm. Never test a third-party system without explicit authorisation. Blockchain projects should document the network, contracts or protocol components, deployment addresses or identifiers where safe, account and key-management approach, transaction lifecycle, oracle or off-chain dependencies and relevant cost or performance decisions.
Projects outside the listed categories should build an equivalent implementation narrative around their actual artefacts and evidence. The guiding question is not “Which template can be copied?” but “What must a reader know and verify to reproduce, operate and evaluate this solution?”
5.4 Testing and Evaluation
Testing should demonstrate whether the implemented system satisfies its requirements and whether the project objectives were achieved. Begin with the test strategy, then present test cases, results, interpretation, defects and retesting. The general concepts in ISO/IEC/IEEE 29119-1:2022 can help distinguish test planning, design, execution, reporting and incident management.
5.4.1 Test Strategy and Acceptance Criteria
Define the purpose, scope, environment, test data, responsibilities and completion criteria before presenting results. Select complementary test levels and techniques because they answer different questions: unit testing checks individual components, integration testing checks interfaces, system testing checks the complete solution, and user acceptance or usability testing checks fitness for intended users where applicable.
Use black-box, white-box or grey-box techniques according to the available knowledge and test objective; they are perspectives, not substitutes for test levels. Include positive, negative, boundary and exception cases. Add performance, reliability, compatibility, accessibility, security or recovery tests when the corresponding requirements exist.
Map every important test to a requirement, feature or objective. Record the tool and version, configuration, repetitions, workload and acceptance threshold. A test verdict must compare the observed result with a predefined expected result; it must not be assigned because the system appeared to work once.
For web-security testing, the OWASP Web Security Testing Guide provides project-specific test ideas. Use authorised targets, protect evidence and report vulnerabilities responsibly. An automated scanner or an SQL-injection screenshot is not a complete security evaluation; combine suitable review, negative testing and manual verification.
5.4.2 Test Cases, Defects and Retesting
Present repeatable test cases and their observed outcomes. Table 5.3 is a suitable template. Test data must be lawful, non-sensitive where possible, and sufficiently described for another authorised evaluator to repeat the test. Replace the illustrative rows with cases from the actual project.
Table 5.3: Test cases and results

Test ID
Traceability
Scenario, data and conditions
Expected result
Actual result, evidence and verdict
TC-001
FR-01 / Authentication
Valid and invalid credentials; include boundary and negative inputs.
Authorised users gain permitted access; invalid input is rejected safely.
Record the observed result, evidence reference and Pass/Fail.
TC-002
NFR-01 / Performance
State the workload, device and network conditions, tool and repetitions.
State the measurable threshold defined in the requirement.
Report the measured result, evidence reference and Pass/Fail.


Where many tests exist, summarise them by module or requirement and place detailed logs in an appendix or repository. Record failed tests, defect identifiers, corrective changes and retest outcomes. Do not delete or conceal a failed result merely because a later version passed.
5.4.3 Project-Type-Specific Evaluation
General software and information systems — report functional coverage, user acceptance or usability evidence, performance, reliability, security and data-integrity results that correspond to the requirements.
AI and machine learning — compare against a meaningful baseline; report task-appropriate metrics, class-wise or subgroup results where relevant, confusion or error analysis, variation across runs or folds, and final held-out test performance. Explain false positives, false negatives or other consequential errors.
IoT and embedded systems — report component and circuit tests, calibration or measurement error, communication range or packet delivery, latency, power behaviour, recovery from disconnection and end-to-end scenario results.
Cybersecurity — report coverage, detection or prevention effectiveness, false positives and false negatives, time to detect or respond, resource overhead and safely reproduced attack scenarios where authorised.
Blockchain or distributed systems — report smart-contract or protocol correctness, access and key controls, transaction success, cost, latency, throughput, finality and behaviour under defined failure or network conditions.
Human-centred or decision-support systems — include usability, accessibility, task completion, user acceptance and appropriate human-oversight evidence in addition to technical performance.
5.4.4 Results Presentation and Interpretation
Use tables for precise comparisons and figures for patterns, distributions, trends or error analysis. A figure should show an insight, not merely that a notebook or test tool was opened. Number and caption each table and figure, state the test conditions, and discuss what the result means for the requirement, objective and intended user.
Separate the expected result from the observed result. Report sample size, repetitions and variability where they affect interpretation. Do not generalise beyond the evaluated environment or population, and do not fabricate results, logs, screenshots, users or measurements.
5.5 Version Control and Implementation Evidence
Provide the project repository link on a readable label such as Project repository and ensure the supervisor can access it. The repository should make development history and reproducibility visible. GitHub repository guidance explains the role of repositories, branches and collaboration, while GitHub flow provides a simple branch-based workflow.
Include a clear README with the problem, setup, configuration, run and test instructions; meaningful commits linked to implemented work; justified branches and pull requests where used; issues or another traceable task record; dependency and environment files; release tags or versions for important milestones; and an appropriate licence or access statement.
Use a suitable .gitignore and remove credentials, secret keys, personal data, large private datasets and generated build files. If such material was committed, removing the visible file is not enough; rotate the exposed credential and follow the platform’s remediation guidance.
Repository screenshots may support the report, but they do not replace an accessible repository and its history. Explain how the selected workflow supported versioning, experimentation, review or collaboration rather than merely listing branch names.
5.6 Author Oversight and Use of AI-Assisted Tools
Where AI-assisted tools were used, include a short declaration naming the tool and provider, explaining what it assisted with and how its output was checked, and confirming that the student remained responsible for the work. Keep the declaration factual and specific to the actual project; replace the example details with the actual tool and workflow.
✍️ Example
OpenAI Codex was used to assist with code review and language refinement in selected sections of this report. Its suggestions were checked against the source code, test results and cited sources. The student made the final decisions and takes full responsibility for the submitted work.
5.7 Evaluation Results, Discussion and Limitations
Organise this section around the research objectives, important requirements or evaluation questions—not around the order in which screenshots were collected. For each objective, state the implemented output, the relevant evidence, the acceptance criterion, the observed result and what the result permits the study to conclude. Use exact measurements, sample sizes, repetitions and uncertainty where they matter.
Discuss the results rather than repeating tables. Explain why important outcomes occurred, compare them with the selected baseline, Chapter 2 literature or justified expectations where appropriate, and analyse failures and consequential errors. A general software project may discuss requirement coverage and user outcomes; an AI project may discuss baseline differences, error patterns and generalisation; an IoT project may discuss calibration, communication and field conditions; and a security or blockchain project may discuss coverage, overhead, cost and behaviour under defined threats or failures.
State limitations honestly and explain their likely effect on the findings. Relevant limitations may involve data quality or representativeness, participants, devices, infrastructure, deployment duration, operating conditions, security coverage, cost, access, external services or evaluation design. Describe any mitigation already applied, but do not convert an unresolved limitation into a stronger claim. The final synthesis, recommendations and future work belong in Chapter 6.
To-Do: End of the Chapter 5 Session
Agree on the final Chapter 5 structure with the supervisor and retain only the project-type subsections that apply.
Complete the implementation-environment tables using tested versions, minimum specifications, justifications and traceable evidence.
Document the implemented modules, data or experimental pipeline and integrations, and trace them to the Chapter 4 requirements and design.
Prepare the test strategy, acceptance criteria and project-specific test cases, including expected results, actual results, evidence, defects and retests.
Present and interpret the important results using suitable tables, figures, measurements, error analysis and limitations.
Add the accessible repository link, README, version history, relevant branches or pull requests, environment files and reproducibility evidence.
Add a brief declaration of AI-assisted tool use, where applicable.
Verify that the report and repository contain no private data, credentials, fabricated evidence or unsupported claims.
Review the completed chapter, working system, repository and evaluation evidence with the supervisor before submission.
Chapter 5 should allow an informed reader to understand what was built, reproduce the relevant environment and evaluation, follow the evidence, and judge whether the solution meets its stated objectives and requirements.
Chapter 6: Conclusions, Recommendations And Future Works
6.1 Introduction
Chapter 6 closes the chain from the original problem and objectives to the implemented solution and the evidence reported in Chapter 5. It should provide a concise answer to what the project established, what should be done on the basis of the findings, and what credible work remains.
Do not introduce new experiments, features, results or citations in this chapter. Every conclusion, recommendation and future-work proposal must be traceable to evidence, a limitation or an unresolved question already discussed. Keep the sections distinct: conclusions state what the study established; recommendations propose justified action; future works identify research or development that remains to be investigated.
6.2 Conclusions
Begin by briefly restating the problem, purpose and completed solution. Then answer the research questions or objectives in the same order used throughout the report. For each objective, state the strongest relevant result and what it means without reproducing the whole results chapter. End by identifying the project’s contribution and the conditions or boundaries within which the conclusion holds.
✅ Match the Conclusion to the Evidence Route
Software and information systems — conclude using implemented capabilities, requirement coverage, user acceptance or usability, performance, reliability, security and data-integrity evidence.
AI and machine learning — state the selected model or approach, fair baseline comparison, final held-out or external evaluation, important error or subgroup findings, uncertainty and the limits of generalisation. For high-stakes uses, state the role of human oversight.
IoT and embedded systems — conclude using sensing or control accuracy, calibration, latency, packet delivery, power and recovery evidence under the tested operating conditions.
Cybersecurity — conclude within the authorised threat model using detection or prevention effectiveness, false alarms, coverage, response time and resource-overhead evidence



---

## C:\Users\ikari\.codex\attachments\0ad0b45b-13ac-42ba-8969-1288aaf1ecd4\Pasted text.txt

Chapter 4 presents the analysis and design of the proposed system. It explains what the system must do, the quality conditions it must satisfy, the data and interfaces it depends on, and the diagrams used to communicate the system’s structure and behaviour.
Keep the introduction concise. Briefly outline the sections covered, identify the analysis and design diagrams included, and restate the development paradigm or combination of approaches justified in Chapter 3—for example, Object-Oriented Analysis and Design (OOAD), Structured Systems Analysis and Design (SSAD/SSADM), or a justified data-centric, experimental or hybrid approach. The selected diagrams must fit the project rather than being included merely because they appear in a list.
System requirements describe the capabilities, qualities, interfaces, data and constraints that the complete system must satisfy. They are not limited to the minimum hardware or software configuration needed to install an application. Requirements should be clear, relevant, feasible, testable and traceable to the problem, objectives, system features and evaluation plan. The requirements-engineering guidance in [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) applies across different project sizes, products and development methodologies.
You may introduce the section using a statement such as: “The system requirements identified for this project are presented in the following subsections.”
- Give each requirement a unique identifier, for example FR-01, NFR-01, DR-01 or IR-01.
- Write one clear requirement per statement and avoid vague words such as fast, secure, user-friendly or efficient unless they are supported by measurable criteria.
- Identify the relevant stakeholder, source or rationale where this is useful.
- State how the requirement will be verified through inspection, demonstration, testing, measurement or user acceptance.
- Maintain alignment among requirements, objectives, diagrams, implemented features and test cases.
Where practical, maintain a compact requirements catalogue containing the requirement ID, statement, priority, source or rationale, and verification method. Do not invent thresholds simply to make a requirement appear measurable; justify them using stakeholder needs, the intended operating environment, authoritative guidance, benchmarks or experiments.
Functional requirements describe what the system must do under specified conditions. They define services, behaviours, business rules, inputs, outputs and interactions that allow users or external systems to accomplish particular tasks.
Examples of correctly framed functional requirements include:
- FR-01: The system shall allow an authorised user to create an account and authenticate before accessing role-specific functions.
- FR-02: The system shall allow a user to search for and retrieve records using the defined search criteria.
- FR-03: The system shall notify the affected user after a specified transaction has been completed or rejected.
In your own documentation, list and explain only the functions required by your project. If you organise the system into modules—such as authentication, file transfer, data collection, reporting or administration—describe the actor, trigger, expected behaviour, output and important exceptions. The requirement should state what is required; detailed implementation evidence belongs in the implementation chapter.
Non-functional requirements describe how well the system must operate and the constraints under which it must work. Select only the quality characteristics relevant to the project. [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) provides a current product-quality model that can help students identify suitable quality areas.
Possible areas include:
- Performance efficiency, including response time, throughput and resource use.
- Security and privacy, including authentication, authorisation, confidentiality, integrity and accountability.
- Reliability and availability, including recovery from failures and continuity of service.
- Usability and accessibility for the intended users and operating context.
- Compatibility and interoperability with required platforms or services.
- Maintainability, testability and modifiability.
- Safety, fairness, explainability or human oversight where the project can affect people or other critical decisions.
Use measurable, project-specific statements. Suitable patterns include:
- Under [defined workload and environment], at least [X%] of [specified transactions] shall complete within [Y seconds], as measured using [identified test].
- Only users assigned the required role shall access [specified data or function], as verified through access-control tests.
- The system shall recover from [defined failure] within [specified period] without losing [identified critical data].
For AI/ML projects, model quality, robustness, fairness and explainability may form part of the quality and evaluation requirements. For IoT projects, relevant requirements may include latency, sensor accuracy, connectivity, power consumption and reliability. These examples must still be justified and measured within the actual project context.
Data requirements apply to all project types, not only AI/ML or IoT. They describe the data the system needs, produces, protects and retains.
Discuss the following where applicable:
- Required inputs, outputs, data sources and ownership.
- Data formats, structures, validation rules and permitted values.
- Data quality, completeness, accuracy, provenance and handling of missing or duplicate records.
- Storage, retention, backup, archival and deletion.
- Privacy, confidentiality, consent and access restrictions.
- Transformations, preprocessing and audit information needed to reproduce the work.
Adapt the discussion to the project. AI/ML projects should address datasets, labels, sampling, train/validation/test separation, representativeness and bias. IoT projects should address sensor types, units, sampling frequency, calibration and missing readings. Information systems should describe records, validation and retention, while cybersecurity projects may focus on logs, telemetry, indicators and provenance.
Interface and integration requirements are also general. They describe how users, external services, software components and hardware devices interact with the system.
Discuss the following where applicable:
- User-interface and accessibility requirements.
- APIs, third-party platforms and external data services.
- Authentication or institutional identity services.
- Hardware devices, sensors, gateways and peripheral equipment.
- Communication protocols, message formats and compatibility constraints.
- Timeouts, retries, validation and error handling when an integration is unavailable or returns invalid data.
For example, an IoT project may describe sensor-to-gateway and gateway-to-cloud communication, while an AI project may describe the interface through which a trained model receives input and returns predictions. A conventional information system may instead focus on web, mobile, payment, messaging or institutional-service integrations.
Every important requirement should link back to an objective or stakeholder need and forward to a feature, diagram and test. When a requirement changes, review the affected design and evaluation evidence. Discuss significant changes with the supervisor.
System analysis and design diagrams help students visualise, examine and communicate different aspects of a proposed solution. They support:
- Understanding and validating system requirements.
- Defining the system boundary and external interactions.
- Representing data, processes, behaviour and solution structure.
- Identifying omissions, inconsistencies, risks and design alternatives.
- Communicating with supervisors, users, developers and other stakeholders.
- Supporting implementation, testing, evaluation and future maintenance.
Use the diagram-selection table already provided in this guide to identify the diagrams appropriate to your project and chosen paradigm. The table is a guide, not a checklist requiring every diagram. Confirm the final selection with the supervisor.
OOAD projects will normally use relevant UML diagrams. SSAD/SSADM projects will normally use context diagrams and data-flow diagrams. AI/ML, IoT, blockchain, cybersecurity and other specialised projects may require a justified combination of UML, structured-analysis, data-pipeline, block, network, architecture or state-oriented diagrams.
A context diagram represents the entire system as one process and shows its interactions with external entities. A DFD Level 0 decomposes that system into its major internal processes, data stores and data flows. They are related, but they are not the same diagram.
This section presents the diagrams used to analyse the problem, requirements, actors, processes, data and system boundary. The selected diagrams should be consistent with the paradigm justified in Chapter 3.
For every diagram, use the following presentation pattern:
- Narrative before the diagram: explain what the diagram represents, why it is relevant, its scope and the requirements or objectives it addresses.
- Diagram: use the correct notation and show only the information needed for that view.
- Figure caption: number and caption every diagram according to the course formatting guidance.
- Interpretation after the diagram: explain the important flows, relationships, decisions and implications instead of merely repeating labels visible in the figure.
All labels must remain readable at normal document size. Use consistent names across diagrams and keep the editable source files. A diagram that cannot be read, explained or traced to the project requirements does not provide useful evidence.
A use case diagram provides a high-level view of how external actors interact with the system and which services the system exposes. Identify the system boundary, actors, use cases and associations. Use include, extend and generalisation only when their UML meanings are justified.
The use-case example included in this guide demonstrates the expected narrative–diagram–interpretation sequence. It is an example of a presentation, not a diagram that every student should copy. Each student must develop a diagram based on the actors and functions of the actual project.
- Explain the narrative and relevance of the diagram before presenting it.
- Keep external actors outside the system boundary and use clear verb-based names for use cases.
- Do not add databases, internal code modules or technologies as actors unless they genuinely represent an external interacting system.
- Caption the diagram and interpret its important relationships after the figure.
- Revisit the course formatting tutorial and discuss any uncertain notation with the supervisor.
System design diagrams describe how the proposed solution will be organised to satisfy the analysed requirements. They may show components, classes, data structures, interfaces, deployment, states, networks, hardware blocks, user interfaces or other implementation-oriented views.
Use the same narrative–diagram–interpretation sequence applied in Section 4.3. Each design diagram should make a clear contribution to the project and remain consistent with the analysis diagrams, requirements and terminology.
For projects that use a conventional database, Chapter 4 should normally present a logical database schema rather than a physical storage design. Show the main entities or tables, important attributes, primary and foreign keys, relationships and cardinalities. Explain significant normalisation or integrity decisions where relevant.
A physical schema contains implementation-specific details such as exact DBMS data types, indexes, partitions, storage configuration and performance tuning. Include these details only when they are necessary to justify the design or evaluation and have been discussed with the supervisor.
Do not force a relational schema onto every project. A NoSQL system may instead show collections or documents and explain embedding and referencing decisions. An AI/ML project without a transactional database may require a data-pipeline or feature-store design, while an IoT project may need a telemetry-storage and data-flow design.
The logical-schema example in this guide is the second worked example. Students should use the same style and academic language for whichever design diagrams are appropriate to their projects.
This is guidance for preparing Chapter 4 and is not a heading that students must copy into the final report. Use tools that support the required notation and allow legitimate, clean export:
- [Visual Paradigm](https://www.visual-paradigm.com/features/ai-uml-diagram-chatbot/) — suitable for formal UML, DFD, ERD and architecture modelling; its AI diagramming assistant can generate and refine model drafts.
- [StarUML](https://staruml.io/) — suitable for UML, ERD, DFD, C4 and other software-modelling views.
- [PlantUML](https://plantuml.com/) — useful for reproducible diagram-as-code workflows, especially use case, sequence, class, activity, component, deployment and state diagrams.
- [draw.io/diagrams.net](https://www.drawio.com/docs/manual/) — a strong general-purpose choice for context diagrams, DFDs, architecture, block diagrams and network topologies.
- [Microsoft Visio](https://support.microsoft.com/en-us/Visio/overview-of-visio-for-the-web) — suitable for process, UML, ERD and network diagrams where the required licence is available.
- [Figma](https://www.figma.com/wireframe-tool/) or [Penpot](https://help.penpot.app/user-guide/prototyping-testing/prototyping/) — better suited to UI wireframes, screen flows and interactive prototypes.
- [Mermaid Chart](https://mermaid.ai/) — useful for AI-assisted and text-based flowcharts, sequence diagrams, class diagrams, ER diagrams and architecture views.
Tool pricing, trials and AI availability change, so confirm the current terms before relying on a tool. Export using SVG or PDF where supported, or a clear high-resolution PNG. Keep the editable source file. Do not hide, crop or bypass a watermark; use a properly licensed, institutionally available or open tool.
Student access can support design verification as well as coding. For example, the [Polypane student offer](https://polypane.app/github-students/) supports responsive and accessibility checks, while selected testing tools in the [GitHub Student Developer Pack](https://education.github.com/pack) can help verify browser behaviour. Follow the redemption and usage guidance in the Build Phase; retain editable designs and evidence of the issues found and corrected.
This activity compares your own modelling decisions with AI-assisted diagram generation. The comparison—not the attractiveness of the first AI output—is the main evidence being assessed.
An online project-supervision portal allows a student to authenticate through the university identity service, upload a project document, submit a revision and request a supervision meeting. A supervisor reviews submissions, provides feedback, approves a submission or requests a revision, and confirms meeting requests. A project coordinator assigns supervisors, monitors submission status and schedules proposal or final defences. When a submission, review decision, meeting confirmation or defence schedule is recorded, the system sends a notification through an external notification service. Users may access only the functions permitted by their assigned roles.
Using only the supplied narrative, produce a UML use case diagram. Show the system boundary, external actors, use cases and associations. Use include, extend or generalisation only where logically justified. Do not invent requirements that are not present in the narrative. Return an editable diagram or diagram source where the tool supports it.
- Step 1 — Read the narrative and draw a UML use case diagram yourself using an appropriate diagramming tool. Complete the manual diagram before consulting an AI diagram generator.
- Step 2 — Research at least three AI-assisted diagramming tools or model-based workflows. Compare their notation support, editability, privacy, export quality, cost or access, and reproducibility.
- Step 3 — Select two AI-assisted options and give each the exact same narrative and instruction shown above.
- Step 4 — Record the product, model name if disclosed, access date, exact prompt, number of refinement attempts and any manual corrections. If the underlying model is not disclosed, state that instead of guessing.
- Step 5 — Compare your manual diagram with both AI-generated diagrams using the criteria below.
- Step 6 — Correct the strongest diagram manually before using it in Chapter 4. You must understand and be able to defend every element that remains.
- Step 7 — Discuss the final diagram and your comparison with the supervisor.
- Coverage and traceability to the supplied narrative.
- Correct identification of actors, use cases and the system boundary.
- Correct UML notation and use of relationships.
- Absence of invented or unsupported functionality.
- Readability, organisation and consistency.
- Editability and reproducibility of the output.
- Time, effort and number of iterations required.
- Privacy, transparency and responsible-use considerations.
- Your manually produced use case diagram.
- The two AI-generated diagrams.
- A concise comparison matrix using the stated criteria.
- The corrected final diagram and a short justification for the approach selected.
- The relevant AI-use log entries, including prompts and verification performed.


---

## C:\Users\ikari\.codex\attachments\298e8f1c-0055-476a-9a02-0b640e6d891b\Pasted text.txt

Update the existing Chapter 5 draft to correspond with the attached Chapter 4 amendment guide. Write in my authorial voice, without referring to me as “the student” or “the author”.

These are documentation changes. Distinguish proposed requirements, inspected code, configured deployment behaviour and completed tests. Do not describe proposed controls as implemented or tested without evidence.

1. **Sections 5.2.1–5.2.3: hosting and recovery**
   Confirm the actual Supabase subscription and available backup facilities. The current draft identifies the Free plan, but a live account check is still needed. Supabase’s official pricing excludes automatic backups and point-in-time recovery from Free. Its database backups exclude Storage image objects. Explain the proposed daily encrypted database exports, seven-day backup retention, separate model/configuration copies and exclusion of raw identity images. Report any actual backup and isolated-restoration evidence separately.
   Sources: https://supabase.com/pricing and https://supabase.com/docs/guides/platform/backups

2. **Sections 5.3.2–5.3.4: retention and consent**
   Chapter 4 now proposes 30 calendar days from upload for non-verified images, 180 calendar days after attempt closure for verification metadata, and the existing three-business-day verified-image policy. Compare these requirements against the implementation. The inspected documentRetentionService.js currently skips pending, review and rejected requests.
   Describe the disclosure and consent record only if implemented: account, purpose, notice version, server-generated timestamp, backend enforcement and withdrawal handling. No corresponding consent control or record was found in the inspected frontend, backend or database files. Proposed wording alone does not close DR-08 or DR-09.

3. **Section 5.3.3: human check**
   Describe the existing internal CAPTCHA accurately. backend/src/utils/captcha.js generates five-character challenges, keeps them in process memory, expires them after five minutes and consumes them on the first validation attempt. Password login validates them through authController.js. Do not name an external CAPTCHA provider. Assess the accessible alternative and implications of restarts or multiple backend instances.

4. **Sections 5.2.2 and 5.3.3: CORS**
   Record the actual HTTP and real-time origin configuration. backend/server.js currently combines localhost defaults with FRONTEND_URL values and permits requests without an Origin header through the CORS check. ai-service/app.py uses unrestricted CORS(app). Compare this with IR-12 and report the remaining differences. Keep CORS separate from authentication, server-to-server credentials and WebAuthn origin validation. CORS is browser response-access control, not general API authentication.
   Source: https://expressjs.com/en/resources/middleware/cors/

5. **Section 5.3.5 and testing: SVM fallback**
   The source default is SVM_TIMEOUT_MS = 5000, applied separately to the status and prediction calls. Confirm the deployed setting rather than assuming the default.
   The current accessControlService.js attempts to write a KYC_DECISION_MADE audit event with details.svmFallback = true and details.reason. Inspect matching audit rows and service logs for the four historical placeholder decisions, using request identifiers and timestamps.
   The available decision/score/request exports do not contain those audit reasons. They cover September–October 2026 and do not themselves establish the hosting environment or failure cause. Do not attribute the four decisions to Azure cold starts without matching evidence.
   Report a longer timeout, warm-up or minimum-replica arrangement only if selected and configured. Distinguish cold and warm measurements, status-call failures, prediction-call failures and model unavailability.

6. **Section 5.4: tests and evidence**
   Add tests corresponding to C4-T25, C4-T26 and C4-T27, and extend C4-T18, C4-T22 and C4-T24. Report actual execution dates, environment, expected/actual outcomes and evidence. Keep unexecuted checks explicitly untested. Existing retention tests that confirm non-verified images are excluded do not demonstrate compliance with the new retention requirement.

7. **Section 5.7.3 and references**
   Retain unresolved implementation and verification limitations until evidence closes them. Document the outcome of supervisor/institutional review of the legal basis, biometric processing, impact assessment and overseas hosting; do not invent approval or claim legal compliance.
   Cite Kenya’s Data Protection Act, 2019 and add:
   World Wide Web Consortium. (2021). Web authentication: An API for accessing public key credentials, level 2. https://www.w3.org/TR/webauthn-2/
   Act: https://kentrade.go.ke/wp-content/uploads/2022/09/Data-Protection-Act-1.pdf

Use the existing Chapter 5 structure and preserve supported results. Identify any application changes or missing evidence separately from document edits.


---

## C:\Users\ikari\.codex\attachments\999f6304-7648-46d1-a14e-b43060199e03\Pasted text.txt

10/24/2026, 05:06:40
[2026-10-24 05:06:40 +0000] [6] [ERROR] Shutting down: Master
10/24/2026, 05:06:40
[2026-10-24 05:06:40 +0000] [6] [ERROR] Worker (pid:11) exited with code 3
10/24/2026, 05:06:40
[2026-10-24 05:06:40 +0000] [6] [ERROR] Reason: Worker failed to boot.
10/24/2026, 05:06:39
[2026-10-24 05:06:39 +0000] [11] [INFO] Worker exiting (pid: 11)
10/24/2026, 05:06:39
return _bootstrap._gcd_import(name[level:], package, level)
10/24/2026, 05:06:39
File "/usr/local/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
10/24/2026, 05:06:39
File "/usr/local/lib/python3.12/site-packages/gunicorn/workers/base.py", line 135, in init_process
10/24/2026, 05:06:39
[2026-10-24 05:06:39 +0000] [11] [ERROR] Exception in worker process
10/24/2026, 05:06:39
return util.import_app(self.app_uri)
10/24/2026, 05:06:39
raise RuntimeError("Set VERITY_API_KEY to a random secret of at least 32 characters")
10/24/2026, 05:01:02
File "/usr/local/lib/python3.12/site-packages/gunicorn/util.py", line 370, in import_app
10/24/2026, 05:01:02
[2026-10-24 05:01:02 +0000] [10] [ERROR] Exception in worker process
10/24/2026, 05:01:02
Traceback (most recent call last):
10/24/2026, 05:01:02
File "/usr/local/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
10/24/2026, 05:01:02
File "/usr/local/lib/python3.12/site-packages/gunicorn/workers/base.py", line 147, in load_wsgi
10/24/2026, 05:01:02
File "/usr/local/lib/python3.12/site-packages/gunicorn/arbiter.py", line 608, in spawn_worker
10/24/2026, 05:01:02
File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
10/24/2026, 05:01:02
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
10/24/2026, 05:01:02
RuntimeError: Set VERITY_API_KEY to a random secret of at least 32 characters
10/24/2026, 05:01:02
^^^^^^^^^^^^^^^
10/24/2026, 05:00:44
[2026-10-24 05:00:44 +0000] [10] [INFO] Booting worker with pid: 10
10/24/2026, 05:00:44
[2026-10-24 05:00:44 +0000] [6] [INFO] Listening at: http://0.0.0.0:8000 (6)
10/24/2026, 05:00:44
[2026-10-24 05:00:44 +0000] [6] [INFO] Using worker: sync
10/24/2026, 05:00:44
[2026-10-24 05:00:44 +0000] [6] [INFO] Starting gunicorn 23.0.0
10/24/2026, 05:00:24
[2026-10-24 05:00:24 +0000] [5] [ERROR] Reason: Worker failed to boot.
10/24/2026, 05:00:24
[2026-10-24 05:00:24 +0000] [5] [ERROR] Shutting down: Master
10/24/2026, 05:00:24
[2026-10-24 05:00:24 +0000] [5] [ERROR] Worker (pid:10) exited with code 3
10/24/2026, 05:00:23
File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
10/24/2026, 05:00:23
File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
10/24/2026, 05:00:23
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
10/24/2026, 05:00:23
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
10/24/2026, 05:00:23
self.wsgi = self.app.wsgi()
10/24/2026, 05:00:23
File "/app/wsgi.py", line 8, in <module>
10/24/2026, 05:00:23
mod = importlib.import_module(module)
10/24/2026, 05:00:23
File "<frozen importlib._bootstrap_external>", line 999, in exec_module
10/24/2026, 05:00:23
return util.import_app(self.app_uri)
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/site-packages/gunicorn/workers/base.py", line 147, in load_wsgi
10/24/2026, 05:00:23
^^^^^^^^^^^^^^^
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
10/24/2026, 05:00:23
^^^^^^^^^^^^^^^^^^^
10/24/2026, 05:00:23
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
10/24/2026, 05:00:23
[2026-10-24 05:00:23 +0000] [10] [INFO] Worker exiting (pid: 10)
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/site-packages/gunicorn/workers/base.py", line 135, in init_process
10/24/2026, 05:00:23
self.load_wsgi()
10/24/2026, 05:00:23
File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
10/24/2026, 05:00:23
^^^^^^^^^^^
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/importlib/__init__.py", line 90, in import_module
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/site-packages/gunicorn/arbiter.py", line 608, in spawn_worker
10/24/2026, 05:00:23
File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
10/24/2026, 05:00:23
[2026-10-24 05:00:23 +0000] [10] [ERROR] Exception in worker process
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/site-packages/gunicorn/util.py", line 370, in import_app
10/24/2026, 05:00:23
return self.load_wsgiapp()
10/24/2026, 05:00:23
File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
10/24/2026, 05:00:23
raise RuntimeError("Set VERITY_API_KEY to a random secret of at least 32 characters")
10/24/2026, 05:00:23
Traceback (most recent call last):
10/24/2026, 05:00:23
File "/usr/local/lib/python3.12/site-packages/gunicorn/app/base.py", line 66, in wsgi
10/24/2026, 05:00:23
self.callable = self.load()
10/24/2026, 05:00:23
worker.init_process()
10/24/2026, 05:00:23
RuntimeError: Set VERITY_API_KEY to a random secret of at least 32 character


---

## C:\Users\ikari\.codex\attachments\c59b83a7-6916-4338-8f57-5e04a8f74c8e\Pasted text.txt

Chapter 6 closes the chain from the original problem and objectives to the implemented solution and the evidence reported in Chapter 5. It should provide a concise answer to what the project established, what should be done on the basis of the findings, and what credible work remains.
Do not introduce new experiments, features, results or citations in this chapter. Every conclusion, recommendation and future-work proposal must be traceable to evidence, a limitation or an unresolved question already discussed. Keep the sections distinct: conclusions state what the study established; recommendations propose justified action; future works identify research or development that remains to be investigated.
Begin by briefly restating the problem, purpose and completed solution. Then answer the research questions or objectives in the same order used throughout the report. For each objective, state the strongest relevant result and what it means without reproducing the whole results chapter. End by identifying the project’s contribution and the conditions or boundaries within which the conclusion holds.
- Software and information systems — conclude using implemented capabilities, requirement coverage, user acceptance or usability, performance, reliability, security and data-integrity evidence.
- AI and machine learning — state the selected model or approach, fair baseline comparison, final held-out or external evaluation, important error or subgroup findings, uncertainty and the limits of generalisation. For high-stakes uses, state the role of human oversight.
- IoT and embedded systems — conclude using sensing or control accuracy, calibration, latency, packet delivery, power and recovery evidence under the tested operating conditions.
- Cybersecurity — conclude within the authorised threat model using detection or prevention effectiveness, false alarms, coverage, response time and resource-overhead evidence.
- Blockchain or distributed systems — conclude using protocol or smart-contract correctness, transaction success, cost, latency, throughput, finality and the tested security and network assumptions.
- Hybrid projects — combine the relevant evidence routes and report the weakest important component as honestly as the strongest; a successful interface does not compensate for an unevaluated model, sensor, security control or protocol.
Avoid broad claims such as “the project was successful” unless the defined acceptance criteria support them. Do not claim novelty, superiority, safety, clinical readiness or real-world scalability from a single demonstration or an unfair comparison.
Recommendations should follow directly from the results and limitations and should be written for a named audience such as users, the adopting organisation, system maintainers, developers, researchers or policy makers. Each recommendation should state the action, the responsible audience, the evidence-based reason and any condition or priority that affects implementation.
- Recommend deployment or adoption only within the environment, population and safeguards that were evaluated.
- Recommend infrastructure changes only when measurements show a bottleneck in compute, memory, storage, network, power or response time.
- Recommend data collection, calibration, security hardening, user training, human review or monitoring when a documented error pattern or limitation justifies it.
- Prioritise recommendations and separate essential safeguards from optional improvements.
- Do not disguise an unimplemented feature, an unsupported model change or a personal preference as a finding-based recommendation.
Future works should extend the research rather than repair missing promised work. Select a small number of credible directions that arise from the limitations, error analysis or unanswered questions. For each direction, explain the rationale, the factor that would change, the data or resources required and how the extension should be evaluated. Prioritise the most valuable directions instead of listing every possible technology.
- Software and information systems — longer deployment studies, broader usability or accessibility evaluation, integration with additional systems, stronger recovery testing or evaluation in a new organisational context.
- AI and machine learning — larger or more representative data, external validation, fairness or subgroup analysis, calibration, explainability, robustness, drift monitoring, alternative approaches under a controlled comparison, or deployment evaluation with meaningful human oversight.
- IoT and embedded systems — additional calibration, wider field conditions, power optimisation, communication alternatives, hardware revision, durability testing or longer reliability studies.
- Cybersecurity — broader authorised threat coverage, adversarial or evasion testing, additional environments, longer monitoring, reduced false positives or independent security validation.
- Blockchain or distributed systems — larger network trials, alternative consensus or scaling designs, contract audits, privacy improvements, governance evaluation or sustained cost and performance measurement.
A proposed direction is not automatically valuable because it uses a newer framework, larger model or more expensive device. Link every future work item to the evidence and explain how success would be measured. Confirm scope and feasibility with the supervisor.
- Write a conclusion that answers the problem, research questions and objectives using only evidence already reported.
- State the project contribution and the conditions, population, environment or threat model within which the findings hold.
- Draft audience-specific, actionable recommendations and link each one to a result or limitation.
- Draft a prioritised set of future works, each with a rationale, required evidence and proposed evaluation method.
- Remove new results, citations, unsupported superiority claims and repeated Chapter 5 detail.
- Check the full alignment chain from the problem and objectives to implementation, evaluation, conclusions, recommendations and future works.
- Review Chapter 6 and the final evidence boundaries with the supervisor before submission.
A strong Chapter 6 is brief but decisive: it tells the reader what the evidence supports, what should happen next, and what remains genuinely open for future investigation.
