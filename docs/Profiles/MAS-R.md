---
hide: toc
title: "MAS-R - Resilient Security"
---

MAS-R tries to prevent an attacker from extracting intellectual property, bypassing security controls (e.g., license checks, DRM, authentication) or negatively impacting the ecosystem (e.g. cheating at a game, unlocking paid features for free, …). It incorporates a range of security measures aimed at enhancing resilience against **reverse engineering and tampering (client-side) threats**, such as repackaging or extraction of sensitive data, IP theft (e.g., proprietary algorithms), piracy.

It assumes that:

- the **security controls of the mobile operating system** cannot be trusted (e.g. the device is rooted/jailbroken).
- the **primary user of the device** is viewed as an adversary (e.g. a reverse engineer or cheater).
- **other applications** installed on the device are viewed as an adversary.
- a **third party with or without physical access** is viewed as an adversary.

MAS-R is recommended for

- apps that have a strong need to safeguard their own **business assets and logic**.

For example, in the gaming industry, competitive online games have a strong need to prevent modding and cheating: a large population of cheaters will have a negative impact on the gaming experience and scare away the legitimate player base. MAS-R's anti-tampering controls raise the effort required to cheat, even though they cannot eliminate it entirely.

Note that the absence of any MAS-R measures does not inherently introduce vulnerabilities. Rather, these measures offer additional, threat-specific protection to applications. However, this is provided that these apps also meet the rest of the OWASP MASVS security controls appropriate to their specific threat models. Crucially, **MAS-R is meant to augment and not replace [MAS-L1](MAS-L1.md) and [MAS-L2](MAS-L2.md).** It should not be used standalone but as an extra layer of defense, supplementing the base security controls in a defense-in-depth strategy.

Note that these measures cannot assure a 100% effectiveness, as the reverse engineer will always have full access to the device and will therefore end up succeeding given enough time and resources.
