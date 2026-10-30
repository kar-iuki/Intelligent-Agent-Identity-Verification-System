# Chapter 4 wireframe assets

The chapter contains ten grayscale wireframes as Figures 4.7 to 4.16.
Each figure is supplied as an editable SVG and a high-resolution PNG.
SVG files can be opened in a browser or edited in a vector editor.
They contain placeholder labels, not real applicant records or evaluation results.

## Source mapping

- 4.7: LoginPage.vue, RegisterPage.vue and passkey sign-in controls.
- 4.8: AgentDashboard.vue personal-details step and WorkspaceShell.vue.
- 4.9: AgentDashboard.vue document step and DocumentCaptureStep.vue.
- 4.10: LiveSelfieChallenge.vue.
- 4.11: AgentDashboard.vue progress and outcome states.
- 4.12: AdminDashboard.vue directory, status filters and WorkspaceShell.vue.
- 4.13: AdminDashboard.vue case-detail drawer and decision controls.
- 4.14: AdminDashboard.vue audit list and export dialog.
- 4.15: ManagePasskeysPage.vue.
- 4.16: AdminModelEvaluation.vue.

I use these wireframes as simplified design views of the current system.
Multiple alternative screens/states appear together in Figures 4.7 and 4.11.
The review drawer is expanded for legibility in Figure 4.13.
The chapter explains mobile reflow, state handling and acceptance checks.

## Remaining diagram updates

I have retained Figures 4.1 to 4.6 from the original chapter. I will replace these diagrams after completing the image corrections, retaining the existing figure numbers.

- 4.1: Confirm system boundary and external actors; draw only justified UML relationships.
- 4.2: Use consistent UML multiplicity/ownership notation and identifier terminology.
- 4.3: Account/profile and incomplete-request optionality; required audit and decision fields.
- 4.4: Request/response directions, auth/storage/realtime interactions and hosted boundaries.
- 4.5: Backend coordination, per-step persistence, quality rejection and service-failure paths.
- 4.6: Align the logical schema with Table 4.7, including decision basis, audit context and optional passkey entities.

## Editorial and verification notes

- Original FR-01 to FR-26 and NFR-01 to NFR-15 identifiers are retained with clarified wording.
- Added FR-27 to FR-34, NFR-16 to NFR-20, DR-01 to DR-12 and IR-01 to IR-10.
- Original timing promises lacked an evidence basis; the chapter specifies measurement and does not invent an SLA.
- Requirements describe intended obligations, not completed implementation or passing tests.
- Disclosure, non-verified retention, backup restoration and broad integration retry policy still need explicit evidence/policy.
- I will check consistency with the final approved methodology and objectives when assembling Chapters 1 to 5.
- The manual-versus-two-AI use-case comparison is a separate course activity; its actual diagrams, prompts, outputs and comparison evidence belong in the record of that activity.
- AI assistance: I used Codex for source review, requirements drafting, wireframe preparation and layout checking on 27 and 28 October 2026.
- Chapter pagination starts at 41. I will update the report pagination, contents and list of figures after merging the chapter into the full report.
