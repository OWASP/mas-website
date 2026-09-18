---
hide: toc
title: "MAS-L2 - Advanced Security"
---

MAS-L2 extends [MAS-L1](MAS-L1.md), introducing additional security measures and best practices for mobile apps to address **advanced threats** requiring more rigorous threat modeling and testing strategies.

It assumes that:

- the **security controls of the mobile operating system** cannot be trusted (e.g. the device is rooted/jailbroken).
- the **primary user of the device** is not viewed as an adversary.
- **other applications** installed on the device are viewed as an adversary.
- a **third party with or without physical access** is viewed as an adversary.

MAS-L2 is recommended for

- apps that handle **high-risk sensitive data** and **contain sensitive functionality**

For example:

- **Health-care apps** that store personally identifiable information which could be used for identity theft, fraudulent claims, or other fraud schemes. In the US, relevant compliance considerations include the HIPAA Privacy, Security, Breach Notification, and Patient Safety Rules.
- **Financial apps** that provide access to sensitive information such as credit card numbers or that let the user move funds. These apps warrant additional controls to prevent fraud and typically need to demonstrate compliance with standards and regulations such as PCI DSS, the Gramm-Leach-Bliley Act, and the Sarbanes-Oxley Act.
