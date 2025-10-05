# Project Charter: Pre-qualification

## Team
- **Sponsor**: John Campbell
- **Project Lead**: Brendan Darcy
- **Key Team**: Max Deluca, Zac Barton, Reiyaz Prasai

## Vision
MVP for Prequalification component of ARMATech.

Collect information about the property, local area and sales evidence upfront, to enable a range of data-driven enhancements to the downstream process. Examples of downstream use include but are not limited to:
- IA
- ARMACheck and Bespoke Workflow
- Verification
- Comparable sales selection
- Assessment

Informaiton collected includes the following sources:
- Client - instruction packet
- API - property and mapping APIs
- 3rd party batch - data sourced from third parties and appended to our MAF
- Models - outputs form inferencing Apprise models (Computer Vision, NLP)

Data is coalesced into a consistent schema. Types of data incluldes:
- Use
- Spatial
- Characteristics
- Sales
- Risks
- Local market
- Model outputs

## Scope & Boundaries
**In Scope**
- Data - Client, CLAPIs, Mapping APIs, Landchecker, AON, Existing
- Models - Computer Vision 1.0, Natural Language Processing
- Subject Property

**Out of Scope / Phase 2 Plus**
- Data - nearmap, PropTrack, Domain / Pricefinder, Corelogic Batch
- Models - Computer Vision 2.0, Logistic scores, Comps score
- Comparable sales

## Success Criteria
**Primary**
- Provides useful input to ARMACheck and Bespoke Workflow
- On time delivery
- Successful deployment to production

**Secondary**
- Data, traffic and storage costs less than $150,000 p.a.

## Timeline & Milestones
| **Milestone** | **Description** | **Target Completion Date** |
|-----------|----------------|-----------------|
| **Identify Sources** | Initial scan of the market and internally to identify potentially promising new sources of data, and existing but unused data sources. A shortlift of sources for the MVP. | Done |
| **RFI** | Request for information from external sources. Initial response with what data is available and a shortlisting for RFQ. | Done |
| **API Access** | Gain access to the in-scope APIs. Develop pipeline to generate results and unerstand the data and schemas. | Done |
| **Sample Analysis** | Shortlisted external providers given a sample of addresses for a sample to be analysed. For both sortlisted suppliers and existing data, agree the analysis and generate reporting on a range of factors, including: coverage, quality, accuracy, usefulness, etc. | Mid-August |
| **Decision Gate - Data Sources** | Agree which suppliers to arrange commercials for new data supply. | Mid-August |
| **Pricing** | Request for quote (RFQ) from shortlisted suppliers and finlisation of pricing. | Mid-August |
| **Supplier Commercials** | Finalise commercials and comemnce data feeds. | Mid-September |
| **Design and Architecture** | Determine the architecture of prequalification. This includes: upgrades to address matching, orchestration (SF and/or AWS-Lambda), Logging (SF and/or AWS), External and Internal calls, External periodic feeds, ETL, schema for the outputs and the process to merge and prioiritise multiple. | Mid-August |
| **Build, Test and Deploy** | Productionise the design logic. | Late-October |

## Key Dependencies
- Computer Vision 1.0
- Natural Language Processing Project

## Risk & Mitigation
- Slow contractual negotiations

## Communication
- **Team**: Weekly working group
- **Project Reviews**: Monthly with Max Deluca

**Charter Date**: [Date]
