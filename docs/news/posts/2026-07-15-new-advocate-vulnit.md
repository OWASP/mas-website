---
title: "vulnit Achieves MAS Advocate Status"
date: 2026-07-15
authors: [carlos, sven]
slug: new-advocate-vulnit
---

We are very happy to announce that [**vulnit**](https://vulnit.com/) has officially been granted the **MAS Advocate** status, **the highest recognition possible within the OWASP Mobile Application Security (MAS) project**.

<center style="margin: 30px 0;">
<img style="width: 20%; border-radius: 10px" src="/assets/vulnit-logo.png"/>
</center>

This status isn't handed out lightly. It's reserved for organizations that have demonstrated **consistent, high-impact contributions** over a sustained period, dedicating not just technical resources but genuine commitment and passion to the OWASP MAS project — going beyond occasional contributions, as outlined in our [official guidelines](https://mas.owasp.org/MASTG/0x02c-Acknowledgements/#mas-advocates). The path to MAS Advocate demands at least six months of proven, impactful support, and in reality often much longer depending on the scope and depth of contributions.

## Who is vulnit?

[vulnit](https://vulnit.com/) is a mobile security consultancy specializing in iOS and Android application security assessments, reverse engineering, and security research. Their team's hands-on expertise in runtime analysis, obfuscation, and anti-tampering mechanisms made them a natural fit for some of the most technically complex parts of the MASTG.

Their two primary contributors to the OWASP MAS project are [@jacobocasado](https://github.com/jacobocasado) (Jacobo Casado de Gracia) and [@sgIOlas](https://github.com/sgIOlas) (Sergio García Cabrera), both mobile security specialists who not just ported tests into the MASTG v2, but brought genuine technical depth to every interaction.

<center style="margin: 30px 0;">
<img style="width: 70%; border-radius: 10px" src="/assets/news/vulnit_at_mascon.jpg"/>
</center>

## vulnit's Focus: MASVS-RESILIENCE

From their very first pull request, vulnit targeted the MASVS-RESILIENCE category, which covers the anti-analysis defenses built into hardened mobile applications to detect or resist tampering, debugging, reverse engineering, and execution in non-genuine environments. The v1 MASTG chapters on these topics were some of the most complex in the guide: mixing bypass strategies, effectiveness assessments, and platform-specific detection mechanisms into long prose chapters. So, porting these to v2's atomic format with a single, precise check per test required genuine understanding of the subject matter.

Across 9 v1 test ports, vulnit produced **17 new atomic v2 tests** and **16 runnable demos** — each with verified device output, working Frida scripts, or r2 analysis commands across topics like anti-debugging detection, emulator detection, obfuscation, dynamic instrumentation tools detection, app permissions, sensitive data in text fields and more.

## Reviews That Went Beyond Comments

What set vulnit apart was not only the volume of their advocacy work, but the depth and judgment behind it. They did not approach the MASTG migration as a mechanical porting exercise. Their reviews questioned whether each item still represented a real security risk, whether it should remain a test, and whether the content would be more useful as a knowledge article or technique instead. This critical review mindset led them to challenge assumptions, validate behavior, and push concrete improvements directly into the content.

Their reviews were not limited to approvals, comments, or minor suggestions. In several cases, their review work became hands-on co-development, improving the structure, technical accuracy, metadata, and practical usefulness of the final tests.

Some examples include:

- **PR [\#3809](https://github.com/OWASP/mastg/pull/3809)**: reviewing the MASTG-TEST-0057 port (Sensitive Data in Text Input Fields), @jacobocasado identified that the original test conflated two different analysis approaches into one. He restructured it into a proper static+dynamic pair: the static test uses r2 to look for `isSecureTextEntry` API references in the binary, while the dynamic test hooks `resignFirstResponder` at runtime via Frida to capture which text fields expose sensitive content at the moment of input. He verified the Frida script output on a real jailbroken device running Frida 17.9.7, added the expected output, and wrote the corrected Observation and Evaluation sections.  
- **PR [\#3827](https://github.com/OWASP/mastg/pull/3827)**: after reviewing the iOS hook detection test, @jacobocasado submitted a full rewrite: converting the test from a static check to a dynamic one, aligning it with its Android counterpart, adding concrete iOS API examples (`fishhook`, `substrate`), and documenting expected false negatives for cases where hook detection is implemented in native code that may not be visible at the Java/Kotlin layer.  
- **PR [\#3871](https://github.com/OWASP/mastg/pull/3871)**: @sgIOlas reviewed the File Integrity Checks port, checking the consistency of the Observation and Evaluation sections and validating the technique cross-references.  
- **PR [\#3883](https://github.com/OWASP/mastg/pull/3883)**: in collaboration with Guardsquare, after their implicit intents port (\#3807), @jacobocasado reviewed the content thoroughly and submitted a follow-up to improve the technical accuracy of the test description, tightening the Evaluation section language and adding missing edge cases for intent broadcast scenarios.  
- **PRs [\#3846](https://github.com/OWASP/mastg/pull/3846) and [\#3862](https://github.com/OWASP/mastg/pull/3862)**: in collaboration with NowSecure, they co-authored the iOS App Permissions port (\#3563) and the IPC Sensitive Functionality port (\#3842), both highly detailed and covering both the technical accuracy of the test content and the correctness of the metadata (weakness, profiles, best-practices links).

This pattern shows deep collaboration in practice. vulnit did not simply review completed work from the sidelines, and they did not treat migration as a one to one conversion of old material into the new structure. They worked with other contributors, verified technical claims, questioned whether the content still belonged as a test, and helped decide when a topic should instead become a technique or knowledge article.

**That level of judgment is what made their reviews and self-authored PRs especially valuable.** They improved not only the wording of individual tests, but also the quality of the model behind them. This is exactly the kind of contribution the MAS Advocate criteria calls for, reviews grounded in thorough analysis, constructive feedback, and actionable improvements that demonstrate clear ownership of the topic.

## Active Participation in the MAS Task Force

Throughout their evaluation period, both @jacobocasado and @sgIOlas participated  consistently in the monthly MAS Task Force calls, presenting their work, flagging questions about test design, and proactively following up on issues raised in previous sessions. They always came prepared and contributed to shaping decisions regarding MASTG v2 and OWASP MAS standards in general.

## A Win for Mobile App Security

With NowSecure, Guardsquare, and now vulnit as MAS Advocates, the MASVS-RESILIENCE category — long one of the least-well-documented areas of mobile security testing — now has dedicated expert coverage. The tests vulnit produced and refined will help practitioners, tool authors, and assessment teams work with a rigorous, unambiguous reference rather than the loosely structured narrative they had before.

> vulnit: _"We are proud to contribute to the OWASP MASTG. Having been involved in the world of security certification, we know how important it is to have a reference standard that is available to everyone and developed by passionate people who are always open to suggestions for improvement. Thank you to Carlos, Sven, and the teams at NowSecure and Guardsquare for working alongside us on this journey. We'll continue working to keep MASTG at the cutting edge of mobile security."_

## Congratulations

On behalf of the full OWASP MAS project community, we congratulate vulnit on achieving MAS Advocate status. Their work on the MASTG v2 porting has been exactly the kind of deep, expert, sustained contribution that makes this project better for everyone. We look forward to continued collaboration and to seeing what comes next!

---

_Want to learn more about the MAS Advocate program or get involved? See our [contribution guidelines for MAS Advocates](https://mas.owasp.org/MASTG/0x02c-Acknowledgements/#mas-advocates) or reach out to the project leaders._
