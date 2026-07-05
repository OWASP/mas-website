---
title: "MASTG v2.0.0 is Here"
date: 2026-07-04
authors: [carlos, sven, jeroen]
slug: mastg-v200-release
---

We just released **MASTG v2.0.0**, the first stable, non-beta release of the fully refactored Mobile Application Security Testing Guide. This is a milestone we have been building toward for three years, and it marks the completion of the most significant structural transformation in the project's history.

[https://github.com/OWASP/mastg/releases/tag/v2.0.0](https://github.com/OWASP/mastg/releases/tag/v2.0.0)

<center style="margin: 30px 0;">
<img style="width: 80%; border-radius: 10px" src="/assets/news/mastg_ii.png"/>
</center>

This post explains what MASTG v2 is, how it came to be, and what it means in practice — including how tests are written, how they connect to the rest of the framework, and what changed in this specific release.

## Where We Came From

The original MASTG was written as a narrative guide: long chapters that mixed background, static analysis, dynamic analysis and code examples into a single flow. A chapter on "Testing Universal Links" could run 500 lines. A chapter on "Testing Anti-Debugging Detection" included bypass strategies, effectiveness criteria, and philosophical guidance on what "good enough" protection looks like. This was the right format for a book, and for years it was enormously useful as exactly that.

But the world changed. Organizations started building automation pipelines that needed to reference specific checks, not pages from a book. Compliance teams needed to trace a requirement in MASVS down to a test and from there to a specific piece of code. Tool authors wanted to know which technique a test relied on so they could determine whether their tool automated it. All of this was very hard to do with a narrative guide.

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 5px" src="/assets/news/mastg_v2_timeline.png"/>
</center>

We began redesigning the framework in **2021**, starting with the MASVS.

- In August 2022, the project [rebranded from OWASP MSTG to OWASP MAS](https://mas.owasp.org/news/2022/08/23/project-rebranding-to-owasp-mas/), making explicit what the project had grown into: not just a testing guide, but a full framework comprising MASVS, MASTG, checklists, and a growing community supporting it.

- [**MASVS v2.0.0**](https://mas.owasp.org/news/2023/04/01/masvs-v2-0-0-release/) (April 2023\) provided the structural foundation the MASTG redesign needed. MASVS v2 reorganized requirements around the classic categories (MASVS-STORAGE, MASVS-CRYPTO, MASVS-AUTH, MASVS-NETWORK, MASVS-PLATFORM, MASVS-CODE, MASVS-RESILIENCE) and moved the old L1/L2/R verification levels out of the standard itself and into the MASTG as Testing Profiles backed by concrete scenarios rather than abstract threat levels. The idea: controls stay platform-agnostic and stable; how you test them, and at what rigor, depends on context captured in the tests.
- In October 2023, [MASVS-PRIVACY](https://mas.owasp.org/news/2023/10/10/masvs-privacy/) extended this with a dedicated category and profile for privacy-relevant controls.

The MASTG refactor followed in two public milestones:

- [Part 1 in July 2023](https://mas.owasp.org/news/2023/07/28/mas-testing-profiles-and-mastg-atomic-tests/) introduced atomic tests and the profile system.
- [Part 2 in September 2023](https://mas.owasp.org/news/2023/09/29/mastg-refactor-part-2/) introduced the full modular component model: tests, techniques, tools, and apps as individually addressable, stable-ID components. From there, the work of porting the 90+ v1 tests and building out hundreds of new ones began in earnest.

But even with atomic tests and a modular structure, something was missing: a layer between the high-level, platform-agnostic MASVS controls and the low-level, platform-specific MASTG tests. A MASVS control like "The app employs current strong cryptography and uses it according to industry best practices" is very abstract by design; it says nothing about what a concrete weakness looks like. A test like MASTG-TEST-0352 is very specific to Android anti-debugging and the relevant APIs and attributes involved. What was supposed to connect them?

In July 2024 we introduced the **[Mobile App Security Weakness Enumeration (MASWE)](https://mas.owasp.org/news/2024/07/30/new-maswe/)**: a structured catalogue of specific weaknesses in mobile applications, modeled after the role CWEs play in the broader software security industry. Each MASWE entry identifies a precise, platform-agnostic weakness and connects upward to the MASVS control it violates and downward to the platform-specific MASTG tests that check for it.

With MASWE in place, the full traceability chain was complete:

<center style="margin: 30px 0;">
<img style="width: 60%; border-radius: 5px" src="/assets/news/mas_traceability_chain.png"/>
</center>

Every test in MASTG v2 carries a `weakness: MASWE-XXXX` field in its metadata. Every MASWE entry traces back to a MASVS control. The chain runs from a compliance requirement all the way to runnable code on a real device.

Here's how it works:

1. **MASVS Controls**: High-level platform-agnostic requirements.  

   For example, "The app employs current cryptography and uses it according to best practices." ([MASVS-CRYPTO-1](https://mas.owasp.org/MASVS/controls/MASVS-CRYPTO-1/)).  

2. **MASWE Weaknesses**: Specific weaknesses, typically also platform-agnostic, related to the controls.  

   For example, "use of predictable pseudo-random number generation" ([MASWE-0027](https://mas.owasp.org/MASWE/MASVS-CRYPTO/MASWE-0027/)).  

3. **MASTG Tests**: Each weakness is evaluated by executing tests that guide the tester in identifying and mitigating the issues using various tools and techniques on each mobile platform.  

   For example, testing for "insecure random API usage on Android" ([MASTG-TEST-0204](https://mas.owasp.org/MASTG/tests/android/MASVS-CRYPTO/MASTG-TEST-0204/)). Tests are backed by knowledge articles (`MASTG-KNOW-****`) and best practices (`MASTG-BEST-****`) that provide additional context and guidance for testers. They use techniques (`MASTG-TECH-****`) to perform the test steps.  

4. **MASTG Demos**: Practical demonstrations that include working code samples and test scripts to ensure reproducibility and reliability.  

   For example, a sample using Java's `Random()` instead of `SecureRandom()` ([MASTG-DEMO-0007](https://mas.owasp.org/MASTG/demos/android/MASVS-CRYPTO/MASTG-DEMO-0007/MASTG-DEMO-0007/)). Demos use specific tools (`MASTG-TOOL-****`) to perform the test steps.

## What MASTG v2 Actually Is

MASTG v2 is now a **knowledge graph** of individually addressable, cross-linked components with stable IDs, structured metadata, and defined relationships to other components. The component types are:

| Component | ID Pattern | Count |
| :---- | :---- | :---- |
| Tests | MASTG-TEST-\*\*\*\* | 285 |
| Demos | MASTG-DEMO-\*\*\*\* | 152 |
| Techniques | MASTG-TECH-\*\*\*\* | 167 |
| Tools | MASTG-TOOL-\*\*\*\* | 135 |
| Knowledge | MASTG-KNOW-\*\*\*\* | 140 |
| Best Practices | MASTG-BEST-\*\*\*\* | 72 |
| Apps | MASTG-APP-\*\*\*\* | 28 |

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 5px" src="/assets/news/mas_component_model.png"/>
</center>

This modular approach allows us to maintain and update each component independently, ensuring that the MASTG remains current and relevant. For example, in our previous structure, the MASTG consisted of large test cases within a single markdown file. This was not only difficult to maintain but also made it challenging to reference specific tests; and it was impossible to have metadata for each test.

The new structure divides tests into individual pages (Markdown files with metadata), each with its own ID (`MASTG-TEST-****`) and links to relevant techniques (`MASTG-TECH-****`) and tools (`MASTG-TOOL-****`). This encapsulation ensures that each test is easily referenced and promotes reusability across all MAS components. For example, you can open a test and see what tools and techniques are being used, and soon you'll be able to do the same in reverse: open a tool or technique and see all the tests that use it. This deep cross-referencing can be extremely powerful when exploring the MASTG.

<center style="margin: 30px 0;">
<img style="width: 70%; border-radius: 5px" src="/assets/news/mastg_maswe_test_demo_example.png"/>
</center>

## The New Test Format

The most consequential change in v2 is how individual tests are written.

A v1 test was a "book chapter". It would open with background, explain the mechanism under test, walk through static analysis, then dynamic analysis, often with inline code examples and Frida scripts woven into the prose.

<center style="margin: 30px 0;">
<img style="width: 80%; border-radius: 5px; border: 2px solid white" src="/assets/news/mastg_v1_test_narrative_example.png"/>
</center>

This had many issues. Just to name a few:

- It was hard to automate. A tool could not parse a 500-line chapter and know what to do.  
- It was hard to reference. A compliance team could not point to a specific test for a specific requirement. Sometimes they would reference a chapter, a section (with an anchor), a paragraph, sometimes a sentence.  
- It was hard to fail. A tester could not say "this test failed" without ambiguity. The chapter blended static and dynamic checks, so a tester could pass one part and fail another, but the chapter itself had no clear pass/fail criteria.  
- It had duplicate content. Many tests repeated the same background, the same Frida scripts, the same "how to decompile and analyze an app" instructions, and the same bypass guidance.  
- It was hard to maintain. A change in a technique or tool required updating dozens of chapters.  
- It was hard to review. A reviewer had to read a long chapter and decide whether it was correct, complete, and consistent with other chapters.

### Example: MASTG-TEST-0070 \- Testing Universal Links

The old [MASTG-TEST-0070 "Testing Universal Links"](https://mas.owasp.org/MASTG/tests/ios/MASVS-PLATFORM/MASTG-TEST-0070/) test ran 513 lines. It covered everything in one continuous narrative: entitlement checking, Apple App Site Association (AASA) file retrieval, link receiver method tracing, dynamic analysis with frida-trace and handoff behavior. This test has now become:

- **MASTG-TEST-0370** — Missing Input Validation in Custom URL Scheme Handlers  
- **MASTG-TEST-0371** — Missing Source Validation in Custom URL Scheme Handlers  
- **MASTG-TEST-0395** — Missing Input Validation in Universal Link Handlers

Each can now be referenced independently, automated independently, and fail independently.

<center style="margin: 30px 0;">
<img style="width: 80%; border-radius: 5px; border: 2px solid white" src="/assets/news/mastg_test_0070_deprecated.png"/>
</center>

### Example: MASTG-TEST-0001 \- Testing Local Storage for Sensitive Data

The old [MASTG-TEST-0001 "Testing Local Storage for Sensitive Data"](https://mas.owasp.org/MASTG/tests/android/MASVS-STORAGE/MASTG-TEST-0001/) test ran 152 lines. It covered everything in one continuous narrative: shared preferences, internal storage, external storage, SQLite databases, and content providers. This has now become:

- **MASTG-TEST-0207** — Runtime Storage of Unencrypted Data in the App Sandbox  
- **MASTG-TEST-0200** — Files Written to External Storage  
- **MASTG-TEST-0201** — Runtime Use of APIs to Access External Storage  
- **MASTG-TEST-0202** — References to APIs and Permissions for Accessing External Storage  
- etc.

And this list will keep growing as we continue to add new specific tests for each storage mechanism that were still missing in the v1 guide.

### New MASTG v2 Tests

A v2 test is an atomic check. It has one thing to verify and it has a fixed structure:

- **Frontmatter metadata**: platform (Android/iOS), type (static/dynamic/code/manual/hooks), weakness (MASWE-XXXX), profiles (L1, L2, R), knowledge articles, best practices, APIs involved.  
- **Overview**: describes what the test checks for  
- **Steps**: describes what you do using existing techniques (MASTG-TECH)  
- **Observation**: describes the raw output from your steps, before interpretation.  
- **Evaluation**: describes how you decide the pass/fail condition.

The example below shows this in practice:

- It’s part of the default L1 and L2 security profiles.  
- It’s targeting Android.  
- The importance of the test is explained in MASWE-0007 (“Sensitive Data Stored Unencrypted in Shared Storage Requiring No User Interaction”).  
- The overview links to additional knowledge articles (MASTG-KNOW) and techniques (MASTG-TECH).  
- The steps link to existing techniques (MASTG-TECH).  
- A clear observation and evaluation are given.

<center style="margin: 30px 0;">
<img style="width: 80%; border-radius: 5px; border: 2px solid white" src="/assets/news/mastg_test_0200_example.png"/>
</center>

On top of this we now have demos (MASTG-DEMO) tied to specific tests. They provide working code, expected outputs, and full automation artifacts. See below.

## MASTG Demos

Each MASTG-DEMO consists of the following items:

- A working sample app (Kotlin, Swift, or Objective-C) that exhibits the weakness under test.
- A runnable script containing static analysis command, Frida script, or shell automation  
- A captured `output.txt` showing the exact expected output  
- An Evaluation section confirming what in the output constitutes a test failure

All demos are built and verified automatically on every push via GitHub Actions.

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 5px; border: 2px solid white" src="/assets/news/mastg_demo_0065_sample.png"/>
</center>

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 5px; border: 2px solid white" src="/assets/news/mastg_demo_0065_steps.png"/>
</center>

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 5px; border: 2px solid white" src="/assets/news/mastg_demo_0065_observation.png"/>
</center>

To ensure our guidelines are practical and reliable, we've developed new MAS Test Apps for both Android and iOS.

<center style="margin: 30px 0;">
<img style="width: 70%; border-radius: 5px" src="/assets/news/mastg_test_apps_v2.png"/>
</center>

These simple skeleton applications are designed to embed code samples directly, allowing users to validate and experiment with the provided demos. This approach ensures that all code samples are functional and up-to-date, fostering a hands-on learning experience.

For example, to test for secure storage, [MASTG-DEMO-0002](https://mas.owasp.org/MASTG/demos/android/MASVS-STORAGE/MASTG-DEMO-0002/MASTG-DEMO-0002/) shows how to use dynamic analysis with Frida to identify the issues in the code. The demo includes:

- a Kotlin code sample (ready to be copied into the app and run on a device)  
- the specific test steps for this case using Frida  
- the shell script including the Frida command  
- the Frida script to be injected  
- the output with explanations  
- the final evaluation of the test

You can run everything on your own device and validate the results yourself\! Just clone the repository and navigate to the [demo folder](https://github.com/OWASP/mastg/tree/master/demos/android/MASVS-STORAGE/MASTG-DEMO-0002), install Frida on your [computer](https://mas.owasp.org/MASTG/tools/generic/MASTG-TOOL-0031/) and your [Android device](https://mas.owasp.org/MASTG/tools/android/MASTG-TOOL-0001/#installing-frida-on-android), and follow the steps.

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 5px" src="/assets/news/mastg_demo_0002_workflow.png"/>
</center>

These demos can also be used as experimental playgrounds to improve your skills and practice with different cases as you study mobile app security with the MASTG. For example, you can try to reverse engineer the app and see if you're able to find the same issues as the demo or you can try to fix the issues and see if you can validate the fix.

They are also great for advanced researchers and pentesters to quickly validate certain scenarios. For example, it's very common to find cases where Android behaves differently depending on the version or the manufacturer. With these demos, you can quickly validate if a certain issue is present on a specific device or Android version.

## What This Means in Practice

**For security testers**: Every test now tells you exactly what to run, what to expect, and what constitutes a failure. You do not need to interpret prose or decide which parts of a chapter apply to your engagement. The Steps section is your test procedure. The Evaluation section is your reporting criterion.

**For compliance and risk teams**: Every test maps to a specific MASWE weakness, which maps to specific MASVS controls. You can trace a compliance requirement through the full chain: MASVS control → MASWE weakness → MASTG test. The IDs are stable and permanently resolvable.

**For developers**: The `best-practices` field in each test links to MASTG-BEST entries that describe how to build the control correctly. If your app fails MASTG-TEST-0326 (biometric auth fallback), MASTG-BEST-0031 tells you exactly how to fix it. Knowledge articles linked via `knowledge:` give you the platform-level understanding.

## Thank you!

Thank you to everyone who contributed to this release and to the multi-year effort behind it.

Special thanks to Carlos Holguera ([@cpholguera](https://github.com/cpholguera)), the architect and heart of the MAS project, who kept the vision alive through the years and his persistence that has shaped it into what it is today.

We also want to give special recognition to a group of contributors whose sustained, high-quality involvement had a major impact on MASTG v2. This includes not only code and content contributions, but also review work, technical discussions, task force participation, consistency, and overall project support.

In alphabetical order:

- Dionysis Lorentzos \- [@diolor](https://github.com/diolor)  
- Jacobo Casado \- [@jacobocasado](https://github.com/jacobocasado)  
- Jan Seredynski \- [@serek8](https://github.com/serek8)  
- Jeroen Beckers \- [@TheDauntless](https://github.com/TheDauntless)  
- Sergio García \- [@sgIOlas](https://github.com/sgIOlas)  
- Stefan Bernhardsgrütter \- [@bernhste](https://github.com/bernhste)  
- Sven Schleier \- [@sushi2k](https://github.com/sushi2k)

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 10px" src="/assets/news/mastg_v2_contributors.png"/>
</center>

Many others contributed along the way, and we are grateful for every meaningful contribution that helped move the project forward. Additional contributors and acknowledgements can be found in the release notes for [v2.0.0](https://github.com/OWASP/mastg/releases/tag/v2.0.0), [v1.9.0](https://github.com/OWASP/mastg/releases/tag/v1.9.0), [v1.8.0](https://github.com/OWASP/mastg/releases/tag/v1.8.0), and earlier releases.

We cannot thank our MAS Advocates enough for their continuous contributions of quality content to the MAS project:

- NowSecure  
- Guardsquare  
- vulnIt

## Feedback Wanted

The v2 framework is complete. Now we build on it.

[**View the release on GitHub →**](https://github.com/OWASP/mastg/releases/tag/v2.0.0)

We encourage you to explore the new [MASWE](https://mas.owasp.org/MASWE/), [MASTG tests](https://mas.owasp.org/MASTG/tests/) and [MASTG demos](https://mas.owasp.org/MASTG/demos/). Your insights and experiences are invaluable to us, and we invite you to **share your feedback** in our [GitHub discussions](https://github.com/OWASP/mastg/discussions/categories/maswe-mastg-v2-beta-Feedback) to help us continue to improve. This way we can ensure that our resources are practical, reliable, and valuable for real-world application.

You can also **contribute to the project** by creating new weaknesses, tests, techniques, tools, or demos. We welcome all contributions and feedback, and we look forward to working with you to make the MAS project the best it can be.  
