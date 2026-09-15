# MAS Testing Profiles

In the realm of mobile app security, adopting a structured and systematic approach is essential to ensure the robustness and resilience of mobile apps against ever-evolving threats. To address this need, the [OWASP Mobile App Security (MAS)](https://mas.owasp.org/) project provides a set of testing profiles that serve as comprehensive frameworks for verifying and enhancing the security of mobile apps.

The **MAS Testing Profiles** outline a series of security controls and tests that can be applied to evaluate mobile app security at different levels of assurance, ranging from fundamental security practices to advanced protective measures. With this, the MAS project provides a flexible framework that allows verification of the appropriate security measures based on the app's unique requirements, risk landscape, and compliance needs.

The MAS Testing Profiles can be used in various ways:

- **App Security Assessment**: Security professionals can leverage the appropriate MAS Testing Profiles based on the app's characteristics to conduct comprehensive assessments to identify vulnerabilities, gaps in security controls, and areas for improvement (e.g. cryptography or secure communication best practices).
- **Secure-by-Design Approach**: Developers can use MAS Testing Profiles as a guideline during the app development lifecycle. By incorporating security controls from the chosen profiles into the design and implementation stages, developers can proactively address security requirements and mitigate potential risks from the early stages of app development.
- **Compliance and Risk Management**: Organizations can rely on the MAS Testing Profiles to align with regulatory and compliance standards specific to the mobile app domain. By mapping the applicable security controls and tests to relevant regulations and industry best practices, organizations can ensure adherence to security requirements and demonstrate their commitment to data protection and privacy.
- **App Vetting Process:** Organizations can use the MAS Testing Profiles as the foundation for app vetting processes before deployment on the organization's devices. The profiles would be carefully tailored and potentially extended with organization-specific security requirements to meet their individual security needs and risk tolerance. See ["NIST.SP.800-163r1 \- Vetting the Security of Mobile Applications"](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-163r1.pdf) for more information.

## The MAS Testing Profiles

To maximize the effectiveness of the OWASP MASVS, applications should undergo a threat model to identify relevant threats and select appropriate security controls. When creating a custom profile isn't feasible, default **L1, L2, R, and P profiles** are available.

These profiles provide baseline security and privacy controls that cover a broad range of common threats, helping developers protect their applications even without a comprehensive threat assessment.

The profiles are divided into **two groups**, reflecting the distinct but complementary goals of **security** and **privacy**:

- **Security profiles (L1, L2, R)**: address technical threats and adversarial behavior.
- **Privacy profile (P)**: focuses on protecting users' personal data and ensuring responsible data handling.

### Attacker capabilities at a glance

| Profile | Brief attacker model |
| --- | --- |
| **MAS-L1** | Other applications installed on the device are adversaries. |
| **MAS-L2** | The operating system cannot be trusted, and attackers may have physical access to the device. |
| **MAS-R** | The user of the device is an attacker, including reverse engineers and cheaters. |
| **MAS-P** | Not attacker-centric; focuses on protecting users' personal data and responsible data handling. |

Each profile is described in detail on its own page:

- [MAS-L1 - Essential Security](MAS-L1.md)
- [MAS-L2 - Advanced Security](MAS-L2.md)
- [MAS-R - Resilient Security](MAS-R.md)
- [MAS-P - Baseline Privacy](MAS-P.md)

While these defaults offer a solid foundation and can be effective for teams with limited time or resources, they may not cover unique or advanced threats. For the highest level of assurance, a custom profile based on a detailed threat model remains the recommended approach.

### Examples

<table>
  <tr>
    <th>MAS L1+P</th>
    <th>MAS L1+P+R</th>
  </tr>
  <tr>
    <td>
      <ul>
        <li>No business assets</li>
        <li>Low-risk sensitive data</li>
        <li>No sensitive functionality</li>
      </ul>
      <p><strong>Example sensitive data:</strong> name, email</p>
      <p><strong>Example apps:</strong> News (BBC News), Calendar (Google Calendar)</p>
    </td>
    <td>
      <ul>
        <li>Business assets/logic</li>
        <li>Low-risk sensitive data</li>
        <li>No sensitive functionality</li>
      </ul>
      <p><strong>Example business assets:</strong> IP, ad revenue</p>
      <p><strong>Example apps:</strong> Ad-supported Weather app</p>
    </td>
  </tr>
  <tr>
    <th>MAS L2+P</th>
    <th>MAS L2+P+R</th>
  </tr>
  <tr>
    <td>
      <ul>
        <li>No business assets</li>
        <li>Moderate/High-risk sensitive data</li>
        <li>Sensitive functionality</li>
      </ul>
      <p><strong>Example sensitive data:</strong> location, payment, health, access tokens, API keys, crypto key encrypting user data</p>
      <p><strong>Example sensitive functionality:</strong> medical record upload, in-app purchases</p>
      <p><strong>Example apps:</strong> Messenger, Health, Sport</p>
    </td>
    <td>
      <ul>
        <li>Business assets/logic</li>
        <li>Moderate/High-risk sensitive data</li>
        <li>Sensitive functionality</li>
      </ul>
      <p><strong>Example business assets:</strong> IP</p>
      <p><strong>Example sensitive functionality:</strong> money transfers, in-app purchases</p>
      <p><strong>Example apps:</strong> Banking, Insurance, Game, Entertainment</p>
    </td>
  </tr>
</table>

**Disclaimer:** The examples highlight the most representative profile for the apps and are provided for illustrative purposes only and aim to represent the different MAS profiles and suggested profile combinations. They serve to highlight the high-level differences between each profile.

<center>
<img src="/assets/Images/Chapters/0x03/example_apps_profiles.png" style="width: 40%; border-radius: 5px"/>
</center>

For guidance on how to select and tailor the right combination of profiles for your app, see [Using MAS Profiles](Using-MAS-Profiles.md).
