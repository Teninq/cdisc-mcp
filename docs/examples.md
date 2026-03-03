# CDISC MCP — Example Conversations

Real examples of questions you can ask an AI assistant with the CDISC MCP server connected.

---

## Example 1: Comparing Domains Across SDTM-IG Versions

**Question:**
> What domains differ between SDTM-IG 3.2 and 3.4?

**Answer:**

### New Domains in 3.4 (not in 3.2)

| Domain | Name | Class |
|--------|------|-------|
| **AG** | Procedure Agents | Interventions |
| **ML** | Meal Data | Interventions |
| **BE** | Biospecimen Events | Events |
| **BS** | Biospecimen Findings | Findings |
| **CP** | Cell Phenotype Findings | Findings |
| **CV** | Cardiovascular System Findings | Findings |
| **FT** | Functional Tests | Findings |
| **GF** | Genomics Findings | Findings |
| **MK** | Musculoskeletal System Findings | Findings |
| **NV** | Nervous System Findings | Findings |
| **OE** | Ophthalmic Examinations | Findings |
| **RE** | Respiratory System Findings | Findings |
| **UR** | Urinary System Findings | Findings |
| **SM** | Subject Disease Milestones | Special Purpose |
| **TM** | Trial Disease Milestones | Trial Design |
| **OI** | Non-host Organism Identifiers | Relationship |
| **RELSPEC** | Related Specimens | Relationship |
| **RELSUB** | Related Subjects | Relationship |

### Domains Removed in 3.4 (present in 3.2)

| Domain | Name |
|--------|------|
| **MO** | Morphology |

### Title Changes (same domain code)

| Domain | 3.2 Title | 3.4 Title |
|--------|-----------|-----------|
| CM | Concomitant Medications | Concomitant/Prior Medications |
| DA | Drug Accountability | Product Accountability |
| EG | ECG | ECG Test Results |
| LB | Labs | Laboratory Test Results |
| RS | Disease Response | Disease Response and Clin Classification |
| TR | Tumor Results | Tumor/Lesion Results |
| TU | Tumor Identification | Tumor/Lesion Identification |

**Summary:** 3.4 adds 18 domains and removes 1 (MO). The new domains are primarily organ-system Findings (CV, MK, NV, OE, RE, UR) and biospecimen/genomics domains (BE, BS, CP, GF), reflecting expanded coverage for modern therapeutic areas.

---

*More examples coming soon. Have a useful query? Open an issue or PR to contribute.*
