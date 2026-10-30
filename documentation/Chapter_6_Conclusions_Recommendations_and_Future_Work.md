# Chapter 6 Conclusions Recommendations and Future Work

Intelligent Agent Identity Verification System

## 6.1 Introduction

This project addressed the need to assess an agent's identity during registration and connect the verification outcome to controlled access. Its purpose was to combine document evidence, facial comparison and liveness assessment in an accountable verification workflow. I developed and hosted a system that captures identity evidence, produces six verification scores, classifies cases and provides an administrator review route. The findings establish a functioning implementation and a reproducible synthetic classifier experiment. They do not establish that the system can reliably approve real applicants without human oversight. This chapter draws conclusions against the five project objectives, recommends actions arising from the reported limitations and identifies priorities for further investigation.

## 6.2 Conclusions

### 6.2.1 Investigation of Current Registration and Verification Practice

The investigation of registration and verification practice provided the basis for the system requirements. As recorded in the objective assessment in Section 5.7.1, this objective was addressed through the Chapter 2 literature review and carried into Chapter 4. Its contribution was to define a workflow extending from account registration and evidence collection to a verification decision and administrative handling. The completed implementation demonstrates how those activities can be connected. The evidence does not establish a measured reduction in processing time or staff workload compared with an existing registration process.

### 6.2.2 Identification of Challenges and Fraud Risks

The identified verification challenges informed the image-quality gate, document-text comparison, facial matching, liveness scoring and registration guardrails. These countermeasures were implemented, but their presence does not establish their effectiveness against real fraud. In the fresh synthetic evaluation, the selected classifier verified 43 of 300 Rejected cases and 184 of 300 Manual Review cases. These results show that combining the available scores leaves consequential errors unresolved. The objective therefore informed the system's controls, while the evidence supports continued human oversight and does not establish a real-world fraud-prevention rate.

### 6.2.3 Examination of Existing KYC Platforms

The examination of existing know-your-customer platforms supplied the related-work comparison and research gap recorded in Chapter 2, as summarised in Table 5.15. This objective provided context for the project's development rather than a comparative product trial. Chapter 5 contains no matched operational evaluation against those platforms. The implemented workflow can therefore be presented as the project's response to the identified requirements, without claiming that it is more accurate, faster or more secure than existing KYC products.

### 6.2.4 Development of the Identity Verification System

I implemented the frontend, application backend, AI service and persistent records, and hosted the application across Vercel, Render and Azure with Supabase providing authentication, database and storage services. The recorded live exports contained 12 verification requests linked to complete six-score records and nine decisions whose outcomes matched the associated request status. This supports the implemented path from evidence scoring to stored decisions. Source inspection also established administrator review, access-control and audit mechanisms, although the exports did not independently demonstrate their live enforcement.

The selected decision approach was version 3.0.0 of a sigmoid-calibrated radial-basis-function support vector machine. It achieved 75.800% accuracy and a macro F1 score of 0.654082 on 1,500 fresh synthetic cases. On the same cases, the saved version 2 model achieved 75.733% accuracy and the Decision Tree achieved 75.667%. The version 3 improvement over version 2 was inconclusive because the reported confidence intervals for the accuracy and macro F1 differences included zero. The threshold baseline had much lower accuracy but fewer false verifications, illustrating the trade-off between accepting genuine cases and limiting incorrect approvals. These comparisons support the recorded model selection within the experiment; they do not establish general superiority.

The development objective was achieved for the core implemented and hosted workflow. Full coverage of the amended requirements remains incomplete, particularly for informed collection, non-verified image retention, metadata expiry, recovery and integration controls. Those omissions limit any claim of operational readiness.

### 6.2.5 Testing and Validation of Effectiveness

The testing objective was partly met. The recorded local evaluation passed 46 automated tests, providing evidence for selected classifier contracts, decision handling, passkeys, retention and frontend behaviour. Public endpoint checks established hosted availability, and I confirmed operation of the hosted workflow. However, three exported requests remained pending, no Manual Review decision appeared in the live sample, and the records lacked independent identity labels. These observations cannot establish real-world accuracy or complete workflow reliability.

Manual Review was the weakest classifier outcome, with recall of 27.33%. Across the two non-Verified classes, 227 of 600 synthetic cases were incorrectly verified. The evaluation therefore does not support autonomous approval, and the effectiveness of administrator intervention remains unmeasured. No representative participant usability study, demographic analysis, comprehensive security assessment or timed hosted pipeline benchmark was reported. Passing selected local tests does not resolve those gaps.

### 6.2.6 Project Contribution and Boundaries

The project contributes an integrated identity-verification implementation and a reproducible method for assessing a classifier that combines document and biometric scores. It preserves a distinction between model and threshold decisions and reports consequential classification errors alongside aggregate accuracy. Its strongest evidence concerns selected local software behaviours, stored request-to-decision relationships and model performance under the specified simulator assumptions. The findings remain bounded by synthetic labels, a fixed class mixture, a small live sample and incomplete operational verification. Hosting establishes availability; it does not establish safety, legal compliance, scalability or effectiveness across real applicant populations.

## 6.3 Recommendations

The following actions are prioritised by their importance to responsible use. They address findings and unfinished requirements reported in Chapter 5; they are not claims that the outstanding controls have already been completed.

### 6.3.1 Retain Human Oversight and Restrict Operational Use

The adopting organisation and system administrators should restrict current use to controlled evaluation and demonstration. Before any trial affects real access rights, they should establish authorised human review of proposed outcomes and verify that decisions, access records and audit events agree. Review must cover proposed Verified outcomes as well as cases placed in the Manual Review queue, because the experiment showed that many cases requiring review were classified as Verified. Human intervention is an essential safeguard, but its ability to correct errors must itself be evaluated before wider adoption.

### 6.3.2 Complete Informed Collection and Retention Controls

Before further operational collection of identity evidence, developers and the adopting institution should resolve the notice, applicable consent, withdrawal and processing-basis gaps identified in Section 5.7.3. Developers should complete and test the amended retention requirements for non-verified images, abandoned uploads, metadata and preservation exceptions, including access expiry and deletion retries. The verified-only cleanup tests do not establish these behaviours. The proposed 30-day image and 180-day metadata periods should remain subject to institutional approval, together with biometric-processing and overseas-hosting safeguards; they should not be presented as statutory periods or evidence of compliance.

### 6.3.3 Verify Recovery and Production Controls

System maintainers should inspect the daily Google Drive backup process and demonstrate an isolated restoration before relying on it for recovery. The checks should cover encryption, restricted access, the proposed seven-day expiry, backup contents, model and configuration recovery, record integrity and reapplication of expired-data deletion. This is essential because backup creation was reported but restoration was not tested. Developers should also complete production-origin separation and an accessible human-check alternative, then execute the outstanding failure, origin, consent and human-check scenarios. Source inspection and health responses are insufficient evidence of their deployed behaviour.

### 6.3.4 Establish Operational Evidence Before Optimisation

Developers and maintainers should record the deployed revision, model version, effective configuration and persisted decision provenance for each evaluated run. They should investigate incomplete requests and link fallback decisions to their actual failure causes. Chapter 5 could not determine why four historical decisions used threshold fallback, so infrastructure changes should not be justified by an assumed cold-start problem. Complete the planned cold and warm timing measurements, access-control checks and administrator walkthroughs first. Changes to timeouts, replicas or service tiers should depend on measured bottlenecks and agreed acceptance criteria. Optional performance tuning should follow the essential safeguards above.

## 6.4 Future Work

The following research directions are presented in priority order. They extend the evaluation beyond the completed study. Implementing and testing the outstanding Chapter 4 requirements remains current completion work under Section 6.3. The scope, resources and feasibility of each extension should be agreed with the supervisor before it begins.

### 6.4.1 External Validation of the Complete Verification Pipeline

The highest priority is to evaluate whether the synthetic findings transfer to real applicants. Researchers would require appropriately authorised identity samples, independently adjudicated outcomes and representative coverage of document types, cameras, capture conditions and relevant applicant groups. The principal change would be evaluation of the full capture-to-decision workflow against real ground truth, rather than generated score vectors. A held-out external set should measure per-class performance, both false-verification categories, calibration and subgroup uncertainty. Authorised presentation-attack testing should assess the liveness component separately. Success would depend on predefined error tolerances and consistent performance across the evaluated conditions, rather than aggregate accuracy alone.

### 6.4.2 Evaluation of Review Policies and Periodic Retraining

The low review recall and uncertain improvement over version 2 justify a controlled investigation of decision policies and model updating. Researchers should compare the existing model with recalibrated or more conservative review policies using the same development data and an untouched evaluation set. Required resources include sufficient adjudicated cases, documented error costs and a manageable administrator review capacity. Administrator-confirmed decisions could support periodic retraining after independent label checks; they should not be assumed correct merely because an administrator approved them. Evaluation should report false verifications, genuine-case rejection, review workload and calibration, with uncertainty estimates. Promotion should require a justified improvement at an acceptable review burden, and retain a versioned rollback path.

### 6.4.3 Longer Studies of Usability and Operational Reliability

After the essential controls and baseline checks are completed, a longer supervised study should examine how applicants and administrators use the system over time. This would require representative participants, an isolated or appropriately approved deployment, accessible task scenarios and monitoring across realistic workloads. The extension would assess sustained use and human decision-making, which were not measured in the present study. Outcomes should include task completion, assistance and recapture needs, accessibility barriers, administrator correction of errors, and cold and warm response times. Longer observation should also measure failures, recovery and changes in score or decision distributions. These results would determine whether the workflow remains usable and dependable beyond a short demonstration and whether broader deployment is justified.
