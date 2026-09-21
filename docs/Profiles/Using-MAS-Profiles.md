# Using MAS Profiles

## Selecting and Tailoring MAS Testing Profiles

When it comes to selecting and tailoring MAS Testing Profiles, it is crucial to follow a defense-in-depth approach, understanding that **the goal is not to comply with every profile or every test within a profile**. Instead, you should take into account the app's specific [threat model](https://owasp.org/www-community/Threat_Modeling), functionality, and [data sensitivity](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-122.pdf) to determine the most suitable testing profiles and specific tests to apply. This allows for a focused and efficient security verification process, tailored to the unique characteristics and needs of your application.

For example, some apps might not incorporate certain features, such as server communication, Multi-Factor Authentication (MFA), or biometrics. In such cases, it is unnecessary to apply tests that aren't relevant to the app's functionality. Similarly, if an app's interfaces don't handle sensitive data, they become less critical to secure.

It's important to involve all stakeholders in determining the appropriate level of security assurance based on the app's risk landscape and the potential impact of a successful attack. This collaborative approach aims to strike a balance between robust security and practicality, ensuring that resources are effectively allocated to mitigate the most relevant risks.

## The Security Trade-offs

Adding more security controls from higher MAS profiles can make an app more secure, but it may also increase development cost, affect the user experience negatively, or prevent legitimate users from accessing the app or parts of it. These trade-offs are worth weighing explicitly when deciding how far up the profile stack to go.

### Security vs Cost

MAS profiles should be applied where it makes sense from a risk vs. cost perspective, i.e. where the potential loss from a compromise of confidentiality or integrity is higher than the cost of the additional controls. The potential loss is the negative impact a breach would have on the app's users, data, functionality, reputation, or revenue; the cost is the time, money, and resources needed to implement and maintain the controls. Estimate how likely the app is to be attacked, how severe the consequences of a compromise would be, and how much value the app provides to its users and the business before deciding how far to go.

For example, an app handling sensitive health data might justify [MAS-L2](MAS-L2.md) for strong encryption and authentication, since the potential loss in terms of user privacy, trust, and legal liability is high. An app that only displays public information, such as weather or news, usually doesn't need to go beyond [MAS-L1](MAS-L1.md), since the marginal security benefit wouldn't be worth the added cost.

### Security vs Usability

Some security features make an app more difficult or inconvenient to use, which can affect user satisfaction or retention. Requiring complex passwords or frequent re-verification, for instance, increases security but may frustrate users who expect a fast, frictionless experience. Conflicts between security and usability requirements are best identified and resolved during app design, rather than after launch.

### Security vs Privacy

Some security features require collecting or accessing user data, which can raise privacy concerns of its own. Using SMS as a multi-factor authentication factor, for example, improves security but also exposes a sensitive piece of personal data (the user's phone number). Balance the security and privacy needs of users, and make sure the trade-off complies with relevant privacy laws and regulations.

### Privacy vs Value

Some apps offer more value or functionality in exchange for accessing or sharing user data, which can compromise privacy. Personalized recommendations or location-based discounts, for example, can also expose users to targeted ads or third-party tracking. Users weigh this trade-off themselves when deciding whether to install and keep using an app, so it's worth being transparent about it.

## About Data Protection and Privacy

When using the MASVS and the MASTG, it is necessary to **conduct a thorough threat model of your app** to determine the appropriate MAS profile. In this process, it is crucial to **consider privacy regulations and laws applicable to your organization and country**. The specific nature and sensitivity of the data often dictate the level of protection required, resulting in different MAS security controls across the profiles. For example, high-risk data that never leaves the device might require [MAS-L2](MAS-L2.md) for storage-related tests, but [MAS-L1](MAS-L1.md) could suffice for network-related tests.

As guidance, [NIST SP 800-122](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-122.pdf) offers illustrative impact levels for Personally Identifiable Information (PII). For instance, sensitive information like Social Security Numbers (SSN), medical history, or financial account details is generally deemed more sensitive than non-sensitive data like phone numbers or ZIP codes. Nonetheless, organizations must adapt these impact levels to their specific data and comply with relevant regulations such as the [General Data Protection Regulation (GDPR)](https://gdpr-info.eu/) in Europe or the [Health Insurance Portability and Accountability Act of 1996 (HIPAA)](https://www.cdc.gov/phlp/php/resources/health-insurance-portability-and-accountability-act-of-1996-hipaa.html) in the USA.

Crafting robust policies and procedures for protecting PII confidentiality is essential. Referencing guidelines and regulations alongside the MASVS can help establish comprehensive data protection measures and ensure compliance with privacy regulations.

## References

- [OWASP MAS \- Using the MASVS](https://mas.owasp.org/MASVS/03-Using_the_MASVS/)
- [Threat Modeling | OWASP Foundation](https://owasp.org/www-community/Threat_Modeling)
- [NIST.SP.800-163r1 \- Vetting the Security of Mobile Applications](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-163r1.pdf)
- [OWASP Secure Product Design Cheat Sheet \- The principle of Defense-in-Depth](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Product_Design_Cheat_Sheet.html#2-the-principle-of-defense-in-depth)
- [NIST SP 800-122, Guide to Protecting the Confidentiality of Personally Identifiable Information (PII)](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-122.pdf)
- [General Data Protection Regulation (GDPR) - EU](https://gdpr-info.eu/)
- [Health Insurance Portability and Accountability Act of 1996 (HIPAA) - USA | CDC](https://www.cdc.gov/phlp/php/resources/health-insurance-portability-and-accountability-act-of-1996-hipaa.html)
- [Payment Card Industry Data Security Standard (PCI DSS)](https://www.pcisecuritystandards.org/standards/pci-dss/)
- [Gramm-Leach-Bliley Act (GLBA) - USA | FTC](https://www.ftc.gov/business-guidance/privacy-security/gramm-leach-bliley-act)
- [Sarbanes-Oxley Act of 2002 (SOX) - USA | SEC](https://www.sec.gov/about/laws/soa2002.pdf)
- [Children's Online Privacy Protection Rule (COPPA) - USA](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa)
- [Personal Information Protection and Electronic Documents Act (PIPEDA) - Canada](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/)
- [Protection of Personal Information Act (POPIA) - South Africa](https://inforegulator.org.za/popia/)
- [OWASP MASTG \- Mobile App User Privacy Protection](https://mas.owasp.org/MASTG/0x04i-Testing-User-Privacy-Protection/)
