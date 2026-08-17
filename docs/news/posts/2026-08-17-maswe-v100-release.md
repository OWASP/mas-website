---
title: "MASWE v1.0.0 is Here"
date: 2026-08-17
authors: [carlos, sven, jeroen]
slug: maswe-v100-release
---

We just released [MASWE v1.0.0](https://github.com/OWASP/maswe/releases/tag/v1.0.0), the first stable release of the [Mobile Application Security Weakness Enumeration](https://mas.owasp.org/MASWE/). Two years after we [introduced the beta](https://mas.owasp.org/news/2024/07/30/new-maswe/), every weakness is now fully written, consistently structured and stably numbered.

<center style="margin: 30px 0;">
<img style="width: 40%; border-radius: 5px" src="/assets/maswe_cover.png"/>
</center>

This one was a genuine team effort. The OWASP MAS Task Force pulled the whole catalogue apart, argued about scope, merged what was redundant, wrote what was missing, and put it back together. This post explains what came out of that, what changed since the beta, and why it matters for the work still ahead in MASTG v2.

## Where We Came From

When we [announced MASWE in July 2024](https://mas.owasp.org/news/2024/07/30/new-maswe/), the goal was to fill the gap between high-level MASVS controls and low-level MASTG tests. A MASVS control like "The app employs current strong cryptography and uses it according to industry best practices" is abstract by design. A MASTG test is specific to one platform, one API, one observable outcome. MASWE is the layer in between: the platform-agnostic weakness that explains *why* the listed tests exist.

<center style="margin: 30px 0;">
<img style="width: 60%; border-radius: 5px" src="/assets/news/mas_traceability_chain.png"/>
</center>

The [MASTG v2.0.0](https://mas.owasp.org/news/2026/07/04/mastg-v200-release/) released in June 2026 shipped with every test linked to a specific MASWE weakness, and the full traceability chain became real:

MASVS control → MASWE weakness → MASTG test → MASTG demo.

But the beta catalogue itself was not finished. It had **119 entries, and 89 of them were still placeholders**: a title, some metadata, and draft content with notes to ourselves about what the page should eventually say.

There was also drift: the 30 entries that *were* fully written had been authored over two years by different people with different instincts, and the result was inconsistent in both structure and scope. Some put *Impact* before *Modes of Introduction*. Some wrote *Impact* as a paragraph, others as a list. Some described consequences under *Modes of Introduction*, and testable causes under *Impact*. Some were narrowly scoped to a single API, others spanned half a MASVS category. Several described the same underlying issue from different angles.

That is acceptable for a beta version, but not for something the industry expects to reference by ID.

## What MASWE v1.0.0 Is

**78 weaknesses**, every one fully written:

| Category | Count | ID range |
| :---- | :---- | :---- |
| MASVS-STORAGE | 6 | `MASWE-0001`–`0006` |
| MASVS-CRYPTO | 11 | `MASWE-0007`–`0017` |
| MASVS-AUTH | 8 | `MASWE-0018`–`0025` |
| MASVS-NETWORK | 3 | `MASWE-0026`–`0028` |
| MASVS-PLATFORM | 12 | `MASWE-0029`–`0040` |
| MASVS-CODE | 10 | `MASWE-0041`–`0050` |
| MASVS-RESILIENCE | 15 | `MASWE-0051`–`0065` |
| MASVS-PRIVACY | 13 | `MASWE-0066`–`0078` |

## What Changed Since the Beta

### 1. Consolidation, from 119 to 78

The beta had grown organically, and it showed. Nine separate entries described "unsafe handling of data from X" for nine different values of X. Ten more described missing authentication on ten different kinds of app components. Written out in full, each of those families would have produced a stack of near-identical pages saying the same thing in slightly different words — and would have pushed that duplication straight down into the tests.

To overcome this: **72 weaknesses were renamed and rescoped, 47 were merged into others, and 6 brand-new ones were created.** Some of the larger consolidations include:

- @MASWE-0050 absorbs the entire "unsafe handling of data from X" family — network, backups, external interfaces, local storage, UI, IPC — plus SQL injection, parsing/escaping, and deserialization. Nine beta IDs, merged into one weakness.
- @MASWE-0018 absorbs services, broadcast receivers, content providers, activities, unauthenticated IPC and more. Ten beta IDs, merged into one weakness.
- @MASWE-0007 absorbs initialization vector (IV) misuse, key reuse, and risky padding.
- @MASWE-0047 absorbs risky crypto, non-proven networking APIs, and non-standard auth — and was broadened to cover apps that fail to *leverage* secure platform functionality, not just apps that roll their own.

The six brand-new weaknesses fill gaps the beta simply did not have:

- @MASWE-0040
- @MASWE-0048
- @MASWE-0051
- @MASWE-0055
- @MASWE-0069
- @MASWE-0075

### 2. Stable, meaningful IDs

IDs are now **consecutive and grouped by category**, `MASWE-0001` through `MASWE-0078` with no gaps, in the MASVS canonical order STORAGE → CRYPTO → AUTH → NETWORK → PLATFORM → CODE → RESILIENCE → PRIVACY. Within a category, weaknesses are ordered by their first MASVS control, so all `MASVS-STORAGE-1` weaknesses precede the `MASVS-STORAGE-2` ones.

This means the renumbering was a one-time event, done deliberately before v1.0.0. **From here on, IDs are stable.** New weaknesses get the next free number and will not necessarily be consecutive within their category, but no existing ID will ever move or be recycled, only deprecated and removed if needed.

We want to be mindful of the people and organizations that are already using the MASWE beta, so we are providing a one-time mapping from the beta to the v1.0.0 IDs. This mapping is [only available with the v1.0.0 release](https://github.com/OWASP/maswe/releases/download/v1.0.0/OWASP_MASWE.yaml) and is provided in machine-readable format. The beta mappings will be temporarily included in each MASWE metadata, but they will be removed in an upcoming release.

### 3. A fixed anatomy for every weakness

Every page now follows the same four sections, in the same order, with the same rules:

1. **Overview** — opens with a single-sentence definition in the form *"This weakness occurs when …"*, then 2–5 short paragraphs of plain prose. No code, no test procedures, no mitigations.
2. **Modes of Introduction** — *only* developer-introduced, testable causes. What someone did, or failed to do, that put the weakness in the app.
3. **Impact** — *only* consequences.
4. **Mitigations** — imperative, actionable instructions addressed to a developer.

Each bullet in *Modes of Introduction* and *Mitigations* starts with a **bold short label**, which makes them addressable in review and, as we will see, maps cleanly onto MASTG content.

The discipline that took the most effort was keeping causes and consequences apart. A bullet like *"Hardcoded Keys: Including cryptographic keys directly in the application code, making them susceptible to extraction through decompilation"* has a cause and a consequence welded together. In v1, the cause stays in *Modes of Introduction* and the consequence moves to *Impact*, where it belongs. It sounds pedantic, but it is the difference between a section you can turn into tests and a section you cannot.

We also enforced platform-agnosticism, with a deliberate exception for clarity. It is fine to mention the Android KeyStore and the iOS Keychain as examples of platform-provided key storage, or `SharedPreferences` and `UserDefaults` as examples of general-purpose key-value storage that offers no protection beyond the app sandbox. Those are the clearest way to make the point. It is not fine to name `WebView` and `WKWebView` separately when "WebView" says the same thing. Any mobile platform specifics belong in the MASTG.

### 4. A canonical vocabulary for impact

The *Impact* section in MASWE v1.0.0 became a focused list of consequences — each opening with a label from a fixed vocabulary of ten, and each closing with a *resulting in* clause:

> *Compromise of Sensitive Data · Authentication or Authorization Bypass · Bypass of Protection Mechanisms · Execution of Unauthorized Code · Financial Loss · Compromise of System Integrity and Business Operations · Violation of User Privacy · Loss of User Trust · Legal and Regulatory Non-Compliance · Compromise of Content or UI Integrity*

Equivalent consequences now use identical wording across all 78 weaknesses.

### 5. A requirement for every weakness

Every weakness now carries a single normative sentence stating the positive *requirement* the app must fulfil — the inverse of the weakness:

- @MASWE-0005 → *"The app excludes sensitive data from application logs."*
- @MASWE-0026 → *"The app encrypts all network traffic."*
- @MASWE-0056 → *"The app implements app attestation."*

This gives every weakness a directly usable requirement statement for policies, contracts, and scorecards, without anyone having to negotiate the phrasing themselves.

### 6. Deeper, audited mappings

We also added mappings to help further understand the weaknesses beyond MASWE, including:

- All **24 MASVS v2 controls**
  - were re-verified for all 78 weaknesses against the actual control definitions, not just carried over from the rename.
  - are covered by at least one weakness.
- All **44 risks** documented on [Android's Security & Privacy risks page](https://developer.android.com/privacy-and-security/risks)
  - were reviewed against Android's risk documentation.
  - map to at least one weakness.
- Every item in the "Privacy and security" section of the [Android Core App Quality checklist](https://developer.android.com/docs/quality-guidelines/core-app-quality)
  - were linked to 25 Android-relevant weaknesses using the new named IDs (`Network_Security_Traffic`, `Minimize_Permissions`, `Cryptographic_Algorithms`, …)
  - map to at least one weakness.
- **93 distinct CWEs** are referenced, keeping MASWE anchored to the broader software security ecosystem.

## Why This Matters

**Mobile app security requirements are increasingly written into regulation and certification, not just into pentest reports.** The MASVS and MASTG are already referenced by [Google's MASA program](https://appdefensealliance.dev/masa) via the App Defense Alliance, by [CREST OVS](https://www.crest-approved.org/membership/crest-ovs-programme/), by NIST SP 800-163r1 and SP 800-218, by BSI TR-03161 for eHealth apps, by the ioXt Alliance, and by government bodies like Singapore or India. When a standard is cited in a certification scheme, ambiguity in that standard becomes ambiguity in someone's compliance obligation.

A weakness enumeration is the layer where that ambiguity gets resolved, because it is the level people actually cite. "The app failed MASVS-STORAGE-2" is not a finding anyone can act on. "The app failed `MASWE-0005`, mode of introduction: verbose logging in production" is.

## The Roadmap Hiding in Plain Sight

Here is the part we find most interesting: the MASWE authoring standard says a MASWE is *not* a test, *not* a demo, *not* a platform deep-dive, and *not* a countermeasure recipe. Those live in the MASTG. But the structure we settled on means each weakness now tells us exactly which of those are missing:

<center style="margin: 30px 0;">
<img style="width: 90%; border-radius: 5px" src="/assets/news/mastg_maswe_test_demo_example.png"/>
</center>

**Every *Mode of Introduction* should have a test:** A mode of introduction is, by construction, a developer-introduced condition that is testable — that rule was enforced across all 78 pages. So each one is a MASTG-TEST candidate, usually one per platform.

**Every *Mitigation* should have a best practice:** A mitigation is, by construction, an actionable instruction to a developer. That is precisely what a MASTG-BEST is.

**36 of the 78 weaknesses have no MASTG test at all yet.** Among them:

- @MASWE-0009
- @MASWE-0019
- @MASWE-0030
- @MASWE-0040
- @MASWE-0049
- @MASWE-0054

... and most of MASVS-PRIVACY.

That is not a complaint about MASTG v2. It is the first time we have been able to state the remaining work as a finite, enumerated list instead of a feeling that there is more to do.

If you have ever wanted to contribute to the MAS project but did not know where to start: pick a weakness with no tests, pick one of its modes of introduction, and write the test that detects it. The MASWE page already tells you what the test has to prove.

## Thank You

This release came from a single **pull request containing 186 files**. It was created by consolidating all previous cross-industry feedback and reviews from the OWASP MAS Task Force team. The PR was open for two weeks and received **500 inline review comments** (yes, this puts GitHub PRs to their limits. We generally do not recommend working on such large PRs, but in our situation, it was necessary). We don't want to use that number to impress anyone, but it really speaks to the quality of the release. Nearly every comment was a specific, researched objection to a particular sentence, and the catalog has much improved because of them.

Thank you to everyone in the **OWASP MAS Task Force** who worked through it, in alphabetical order:

- Dionysis Lorentzos — [@diolor](https://github.com/diolor)
- Jacobo Casado — [@jacobocasado](https://github.com/jacobocasado)
- Jan Seredynski — [@serek8](https://github.com/serek8)
- Jeroen Beckers — [@TheDauntless](https://github.com/TheDauntless)
- Sergio García — [@sgIOlas](https://github.com/sgIOlas)
- Stefan Bernhardsgrütter — [@bernhste](https://github.com/bernhste)
- Sven Schleier — [@sushi2k](https://github.com/sushi2k)

Special thanks to Carlos Holguera ([@cpholguera](https://github.com/cpholguera)) for driving the remapping, the consolidation, and the authoring standard that made a catalogue of this size internally consistent.

We also want to thank everyone in the wider community who filed issues, opened discussions, or told us at a conference that a particular weakness did not make sense or could be improved. A lot of the merges in this release started as someone pointing out that two pages were saying the same thing.

And we cannot thank our **MAS Advocates** enough for their continuous contributions:

- NowSecure
- Guardsquare
- vulnit

## Feedback Wanted

MASWE v1.0.0 is live:

- 🌐 [Browse the MASWE](https://mas.owasp.org/MASWE/)
- :simple-github: [OWASP/maswe on GitHub](https://github.com/OWASP/maswe)
- 📄 [The v1.0.0 pull request](https://github.com/OWASP/maswe/pull/182), including the full beta → v1.0.0 mapping

If you have used the beta MASWE IDs, you can consult the mappings to v1.0.0 from here: <https://github.com/OWASP/maswe/releases/download/v1.0.0/OWASP_MASWE.yaml>

And if you want to contribute, [come and talk to us](https://mas.owasp.org/contact/) or jump straight into the [GitHub discussions](https://github.com/OWASP/mastg/discussions). There has never been a clearer map of what is left to build.
