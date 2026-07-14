---
title: "MASTG v2.0.0 Removes MAS Checklists"
date: 2026-07-14
authors: [carlos, sven, jeroen]
slug: checklists-removal
---

With [MASTG v2](https://github.com/OWASP/mastg/releases/tag/v2.0.0), the OWASP MAS project has completed a major structural change in how MASVS, MASWE, and MASTG work together.

Previous MASTG releases included a generated MAS Checklist spreadsheet file. This file was useful for many assessment workflows. It gave testers a familiar way to track status, follow MASVS coverage, and jump from requirements to MASTG tests.

MASTG v2 does not include this spreadsheet file as an official release artifact.

This follows the same direction we already took when discontinuing the PDF version of the MASTG. Static release artifacts such as PDFs and spreadsheets were useful in the past, but they also require significant maintenance. They need dedicated generation logic, formatting, release handling, review, testing, and support. Over time, they can become separate product surfaces that need to be maintained in parallel with the actual project content.

We do not believe this is the best model for MASTG v2.

The industry has moved away from static documents as the primary way to consume technical guidance. Security teams now expect searchable, linkable, structured, continuously maintained content. They need data that can be filtered, mapped, integrated into tools, used in reports, and adapted to different assessment workflows. A fixed PDF or spreadsheet file is often less useful than authoritative structured content that can power many different views.

MASTG v2 was designed with this in mind. Tests, weaknesses, controls, profiles, techniques, tools, demos, knowledge articles, and best practices are now connected through structured metadata. The MAS website and project repositories are the authoritative source.

We recognize that some teams may want spreadsheet views, trackers, dashboards, or internal report templates. Since the source repositories now contain all the relevant data in a structured format, it can easily be ingested in other frameworks or tooling. Different organizations have different reporting needs, and custom generated views may often be more useful than one official spreadsheet.

## Community Feedback

That said, we value community feedback! If the spreadsheet checklist is important to your workflow, we would like to hear from you. The data is available in a structured format already, but maybe there are issues with incorporating this into your workflow and a different format would be better. Please let us know by contributing to the open discussion!

<https://github.com/OWASP/mastg/discussions/3923>

For example, we are also interested in whether an official machine readable data artifact would be more useful than an spreadsheet file. A structured export could give the community a stable basis for building spreadsheets, dashboards, reporting tools, assessment trackers, and AI assisted workflows, without requiring the core project to maintain one specific spreadsheet format.

Existing spreadsheet checklist files from previous releases remain available for historical use. For MASTG v2, the MAS website and project repositories are the authoritative source.
