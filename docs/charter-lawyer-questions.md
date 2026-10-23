# Charter Agreement: Questions and Flags for a California Attorney

> **DRAFT FOR ATTORNEY REVIEW. NOT LEGAL ADVICE.** Prepared by an AI drafting assistant. Checklist of issues to have a California attorney confirm before any venue signs `charter-agreement-DRAFT.md`. Sources loaded by the drafter are marked; everything else is from general knowledge and unverified.

## A. Entity, authority, execution
1. **Entity/DBA and signing authority.** Is "Insert" a registered entity or a DBA of Dillon personally? *Why:* a sole proprietor has unlimited personal liability, and the liability cap and indemnities only help if the contracting party is right. Also confirm who may sign for each venue (owner vs. manager, LLC vs. individual).
2. **E-signature approach.** Is a clickwrap/DocuSign signature enough, and should the offer page's "Apply" step include any binding language? *Why:* enforceability and a clean audit trail. Also confirm the Agreement (18.1) can supersede website statements, and whether the website's "after the charter period" wording needs fixing.
3. **Selection by application.** Any issue with turning applicants down or limiting to two seats (Section 2.6)? *Why:* low risk, but confirm no implied promise.

## B. Messaging law
4. **TCPA exposure and who is the "sender."** Texts go out in the venue's name, via Insert's platform. Who bears TCPA risk, and does the Section 6 allocation hold up? *Why:* 47 U.S.C. § 227 (loaded: https://www.law.cornell.edu/uscode/text/47/227; the drafter read only the amendment notes, not the full consent/damages text) is the basis for statutory damages per message, which can dwarf a $3,600 liability cap. Ask whether Insert, as the party that actually transmits, can be a direct defendant, and what consent language is needed for inquiry-triggered texts vs. later reminders and review requests.
5. **CAN-SPAM.** Confirm Section 6.3's transactional/promotional split and whether tour/deposit reminders and review requests are "commercial." *Why:* the FTC guide (loaded: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) says CAN-SPAM covers all commercial email, with no B2B exception, and states penalties up to $53,088 per email; it also treats the sender and the party whose product is advertised as responsible. Ask who counts as the "initiator" here.
6. **SMS carrier registration (10DLC) and A2P rules.** Who registers and in whose name? *Why:* unregistered traffic is blocked and carrier rules act like contract terms. Unverified; not researched.

## C. Privacy and AI
7. **CCPA/CPRA service-provider terms.** Does Section 8 satisfy the required contract terms (limits on selling/sharing, use outside the direct relationship, combining data, audit and compliance notice, subprocessor flow-down)? Is the venue even a "business" under the thresholds, and does it matter? *Why:* the wrong contract terms can make the venue treat Insert as a third party. Statute (Civ. Code § 1798.140 and regulations) **was not loaded** (fetch returned 403); verify.
8. **Wedding data nuances.** Some inquiries mention guests, religion, or health/accessibility. Does that create sensitive-information issues? *Why:* heightened requirements may apply; Section 8.9 only bans sending IDs, card or health data.
9. **AI disclosure and guardrails.** Must replies disclose they are AI-drafted? Section 7.1 leaves it open. *Why:* Cal. Bus. & Prof. Code § 17941 (bot disclosure, relevant for bots that incentivize a sale) **was not loaded** (403); also FTC deception risk if a reply implies a human wrote it. Ask also about the no-training promise in 7.5 and whether it depends on provider terms that can change.
10. **Data breach notification.** Confirm the 72-hour commitment and who notifies individuals under California's breach statute. Unverified.

## D. Money and risk
11. **Limits of liability enforceability.** Is a 12-month fee cap ($3,600) plus consequential-damages waiver enforceable in California, and are the carve-outs right (Civ. Code § 1668 is cited from memory, not loaded)? Should data breach and indemnities have a separate or higher cap? *Why:* a cap that is unconscionable or too broad can be struck; carve-outs for fraud, gross negligence and statutory violations are typical.
12. **Early-termination amount (Section 5.3).** Remaining fees through month six: enforceable liquidated damages or a penalty? Consider 50% instead. *Why:* California looks hard at penalty clauses.
13. **Refund/credit policy.** Is the free-day credit (Section 3.3) and the pro-rata credit for downtime (4.6) clear and workable? Is "billing starts at go-live" plus "delay billing day for day" meaningful (it is a credit in the draft because billing already starts at go-live)? *Why:* avoids an ambiguity that favors the venue.
14. **Sales tax on SaaS in California.** Is the $300/month service subject to sales/use tax, or is it a non-taxable service? *Why:* getting it wrong creates a back-tax liability. The drafter loaded CDTFA Publication 109 (https://cdtfa.ca.gov/formspubs/pub109/) but it concerns **tangible goods sold over the internet** and does not answer this. **Unsure.** Ask a CPA or CDTFA.
15. **Insurance.** Does Insert need cyber/tech E&O coverage, and should the venue's general liability be required? *Why:* a data or messaging incident can exceed the cap; many venues' insurers or landlords ask for certificates.

## E. Structure and IP
16. **Free build and employment/IP issues.** Does a free build in exchange for feedback and a testimonial create any employment-like, barter-income or tax characterization? Does Insert's ownership of the software and "no work-for-hire" (9.3) fit what the venue expects, and should the venue get an exit licence to its own templates? *Why:* the free build has value; testimonial exchange can trigger FTC endorsement disclosure duties (16 C.F.R. Part 255, not loaded) and income-reporting questions.
17. **Testimonial and name/logo clause.** Is the revocable, separate-approval structure (11.3) workable, and is it an issue that a testimonial is an expected "in return" item on the website? *Why:* endorsement rules and a possible "paid review" appearance.
18. **Non-exclusivity and territory.** Decide whether to offer venues a no-nearby-competitor promise (Section 12). *Why:* a commitment venues will ask for; also check antitrust-style concerns of exclusivity.
19. **Dispute forum.** County placeholder, arbitration vs. court, attorneys' fees (Section 17). *Why:* cost vs. a $300/month relationship.
20. **Payment handling.** Confirm that sending only the venue's own payment link, with no money flowing through Insert, keeps Insert out of money-transmitter/payment-facilitator rules, and that "no percentage fee" stays true in all marketing. Unverified.

## F. Drafter's open decisions for Dillon
- Early-exit amount (all remaining fees vs. less).
- Free-month credit size for a missed go-live.
- Price-lock reading versus the website's "after the charter period" wording.
- Default AI mode for the first 30 days (auto vs. human approval).
- SMS fees: passed through or included.
- Fix `venues.html` and any ad copy to match whatever is finally signed.
