---
name: cc-google-play-refund
description: Get Google Play to refund a Claude (Anthropic) subscription that was bought through Google Play when the Claude account was then banned or suspended. Use when the user asks to recover a Google Play charge for Claude Pro or Max after a ban, to write to Google Play support or the Play Help Center about it, or to put together the evidence screenshots. The agent checks the preconditions (and, if Anthropic has not yet refused in writing, helps the user ask Anthropic first), makes one pass through the user's Gmail, asks for all missing screenshots at once, redacts and captions the exhibits, opens the Play Help Center case by email and drafts a complete English message for the user to review. It never sends anything without the user's explicit approval.
license: MIT
compatibility: Needs direct Gmail access (read, and ideally draft or send) and the ability to take screenshots. Bundled scripts need Python 3.8+ and Pillow. OCR redaction is optional and needs pytesseract.
---

# Google Play refund for a banned Claude subscription

The goal is a refund of one Google Play order (`GPA.xxxx-xxxx-xxxx-xxxxx`) for a Claude subscription. It works best once Anthropic has refused the refund in writing; Step 1 helps get that answer if it is missing. Google Play billed the user, so Google Play can refund the order. The strategy, learned from experience: **make the first full message complete**, so that a Google Play support specialist has everything they need in a single read. Stating all the necessary information up front speeds things up and keeps follow-up rounds few or none. Some information proved especially effective at turning points: the developer's written refusal quoted verbatim, a minute-precise purchase-to-ban timeline, the original ban notice, a clear argument for who should refund, and annotated exhibits. A refund is never guaranteed; Google decides case by case.

## Ground rules (apply throughout)

1. **No templates.** This skill deliberately contains no reply template. Support systems detect and deflect boilerplate. Write the message fresh from the user's own facts, in your own words, following the *Required information* list below. Never reuse wording from another case or from examples.
2. **Aim for a complete first message.** The goal is that few or no follow-ups are needed: put all the required information into the first full message instead of spreading it over several replies. Follow-ups are fine when needed; each one should respond to what Google actually said and carry the information that answer needs.
3. **The user approves before anything is sent.** Show the full draft and the attachment list, then wait for an explicit "send". Never submit a form, send an email or post a reply on your own.
4. **Ask for the refund of this order, to the destination the user chose.** The user picks the refund destination (Step 6); the message states it. Do not add alternative demands, deadlines, threats or references to any other process or venue.
5. **Privacy.** Redact anything not needed for the case (see Step 4). Never put the user's data anywhere except their own drafts and exhibit files.
6. **English, polite, factual.** Write as the user, in the first person. Be courteous and specific. Do not speculate about why the account was banned and do not argue about the ban itself. The case is about a payment for a service that could not be used.

## Step 0 - Capability check (before touching anything)

You need both of the following. Check them now, not halfway through:

| Capability | Why | How to check |
|---|---|---|
| **Direct Gmail access** for the Google account that made the Play purchase: search, read full messages with headers, and ideally create drafts or reply in a thread | Find the receipt, the ban notice, the Anthropic thread and any Play support thread. Attach exhibits to the reply. | Run a harmless search such as `from:googleplay-noreply@google.com` and open one result |
| **Taking screenshots yourself** (a browser or computer-use tool, or headless Chrome rendering an email you fetched) | Exhibits should be captured by you, consistently, with the address bar and the time visible | Take one test screenshot of any page |
| **Image editing** | Redact and caption exhibits with `scripts/redact.py` and `scripts/annotate.py` | `python3 -c "import PIL"`. If it fails: `python3 -m pip install --user Pillow` |

If Gmail access or screenshots are missing, **do not hardcode an install method.** Find out which agent host you are running in (Claude Code, Cursor, Codex, another IDE or CLI agent, a desktop app). Search the web or that host's docs for the current ways to add a Gmail integration (an official connector, an MCP server, a plugin or extension) and a browser or screenshot tool on that platform. Then give the user 2 to 4 concrete options with their trade-offs (official or third-party, permissions requested, setup effort). Let the user choose and help them set it up. If nothing workable exists, say so plainly. The fallback is that the user takes screenshots by hand following the rules in Step 3, and you still do the rest.

## Step 1 - Preconditions and triage

Check these from the mailbox before going to Google Play. Tell the user which ones are met.

1. **The Google Play receipt** for the Claude subscription (order number `GPA.…`, amount, the order time, the Google account and the payment method on the receipt).
2. **The ban or suspension notice** from Anthropic (email and/or the in-app or web notice). The Claude login email may differ from the Google Play account. That is fine, but note both addresses.
3. **A written answer from Anthropic** about refunding this Play order. "Written refusal" means a sentence such as "we are unable to issue a refund". An automated acknowledgement or "still in queue" is not an answer.

**Triage when item 3 is missing.** It matters because Google Play's standard first answer is "contact the developer". Help the user ask Anthropic first:

- Channels: the Claude Help Center at https://support.claude.com (signed in: name or initials, then **Get help**, which opens the support messenger; the [refund article](https://support.claude.com/en/articles/12386328-request-a-refund-for-a-paid-claude-plan) describes the flow), or email **support+android@anthropic.com** (the developer contact on the Claude Play Store listing). If the account itself should be reinstated, that is a separate appeal: log in at claude.ai with the banned account and use the appeal form ([Safeguards warnings and appeals](https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals)).
- Content: ask for a refund of this specific order. Include the order number, purchase and ban dates and times, amount and currency, the Play account email and the Claude login email, and a one-line reason.
- If Anthropic asks for proof of ownership, such as CCing the Google Play email, do exactly that.
- A written answer usually arrives within days. Then:
  - **Anthropic refunds it:** done. This skill is not needed.
  - **Anthropic refuses in writing:** continue with Step 2.
  - **No answer after about 7 days and one polite follow-up:** the user can still go to Google Play, documenting the request and the follow-up with dates. The case is weaker but possible.

**Not bought through Google Play?** This skill does not apply. iOS (App Store): Apple refunds, at https://reportaproblem.apple.com. Web (claude.ai): ask Anthropic through the Claude Help Center (Get help, then the refund request).

## Step 2 - One exploration pass of the mailbox

Do one thorough pass and write down every fact you will need. Useful searches (adapt them to the mailbox language):

- `from:googleplay-noreply@google.com` (receipt, "subscription will be canceled", refund request received or denied)
- `"GPA."` and the order number once you know it
- `from:anthropic.com` or `from:mail.anthropic.com` (suspension notice, support replies)
- `"unable to issue a refund"`, `refund`, `suspended`, `Claude Max`, `Claude Pro`
- `from:googleplay-support@google.com` (an existing Play support case, with its case ID in the subject)
- The user's sent mail to Anthropic (proves they followed Google's "contact the developer" instruction)

Build a private **case sheet**. Keep it in the chat or a scratch file outside any repository, never in this skill's folder:

- Google Play account email; Claude login email (if different)
- Order number; product name; amount and currency; payment method as shown (last 4 digits only)
- Purchase time, **to the minute with the timezone**; also convert it to UTC
- Ban or suspension time, to the minute with the timezone, in UTC as well; the **gap between purchase and ban** (call it out if it is short: minutes, hours or a few days)
- The time of Google Play's cancellation notice, if any (it often arrives in the same minute as the ban)
- Earlier Play refund requests and their outcomes (dates)
- Every message to and from Anthropic: date and time, who wrote it, and the key sentence. Record the **refusal sentence verbatim** with its date
- Any existing Play support case ID and its latest message
- Anything on Anthropic's side that says the subscription was cancelled or refunded, while no refund actually arrived

Time hygiene: Gmail shows times in the viewer's timezone. Headers and APIs often use UTC, and Google receipts sometimes show Pacific time. Pick one timezone for the message (usually the user's local one), label it every time (for example `14:07 UTC+8`), and put UTC in brackets where it helps. Double-check every conversion.

## Step 3 - List ALL required screenshots in one go

After the exploration pass, decide the complete exhibit list. Tell the user **once** which items you will capture yourself and which ones only they can provide. Do not drip-feed requests. Typical exhibits, in chronological order:

1. Google Play order receipt
2. Anthropic's ban or suspension notice (email; plus the in-app or web notice if one exists)
3. Google Play's subscription-cancelled notice (if any)
4. Earlier Google Play refund decisions (if any)
5. The user's refund request(s) to Anthropic
6. Anthropic's written refusal(s), plus any ownership or verification steps they asked for
7. Anthropic's own statement about cancellation or refunds on ban, if any (for example on the account's restricted page)
8. The latest Google Play support reply, if a case already exists
9. Optionally, one Gmail search-results overview showing that the case emails exist (see the redaction rule below)

Screenshot rules (all mandatory):

- **Inbox or list views:** mask every row that is unrelated to the case before using the image.
- **Anything not captured in Gmail** (the ban notice in the Claude web or desktop app, another mail provider, a phone screen) must show the **browser address bar or app context, the current time, and the account or recipient** it belongs to. A phone screenshot must include the status-bar clock.
- **Gmail messages:** show the From, To, Date and Subject headers. Expand "show details" if needed so the exact time is visible. Rendering the message from its raw data in a clean page with the headers is fine, as long as the content is unedited.
- Capture full resolution and do not crop away timestamps or senders.

When you ask the user for items only they can provide, give the whole list in one message: what to open, what must be visible, and what to hide.

## Step 4 - Prepare the exhibits (redact, then annotate)

Script paths below are relative to this skill's folder, the one that contains this SKILL.md. Claude Code expands `${CLAUDE_SKILL_DIR}` to it. Elsewhere, use the folder where the skill was installed.

For each image, in this order:

1. **Find coordinates.** Run `python3 scripts/grid.py in.png /tmp/in.grid.png` and look at the grid copy. Never send the grid copy.
2. **Redact.** Use `python3 scripts/redact.py in.png step1.png --band Y1,Y2 ... --rect X1,Y1,X2,Y2 ...`
   - Unrelated inbox rows: `--band` (optionally limited with `--band-x`)
   - Card numbers except the last 4 digits, full addresses, phone numbers, other people's names and emails, avatars, tokens and links with tokens in them
   - Full email addresses may be partly masked if the user wants. Keep enough of them to show that the Play account and the Claude account match the case sheet
   - Optional automatic pass: `--ocr "REGEX"` (needs pytesseract). Always check the result by eye
   - Use the default `black` mode for anything sensitive. Blur and pixelate are for cosmetics only
3. **Annotate.** Use `python3 scripts/annotate.py step1.png NN-name.png --title "Exhibit N - <what it is>" --caption "<exact time with timezone>; <what it shows and why it matters>"`. Add `--box`, `--arrow` or `--note` to point at the key line, such as the refusal sentence, the timestamp or the order number. For complex layouts, use `--spec file.json` (see `examples/demo-spec.json`).
4. **Look at the final image** to confirm nothing sensitive is left and that the caption is right.

Every exhibit gets an English banner with its number, the exact time with the timezone, and one sentence on what it shows. File names should be `NN-short-description-YYYY-MM-DD.png`. Keep the total attachment size comfortably under the mail provider's limit (Gmail: 25 MB). Use `annotate.py --max-width 1600` or JPEG output if needed.

A worked, fictional example is in `examples/`: `sample-inbox.png` goes through `redact.py`, then `annotate.py`, and becomes `demo-exhibit.png`. `examples/demo.sh` rebuilds it.

## Step 5 - Compose the complete message

Write it from scratch from the case sheet. It must convey all of the following. The order and wording are yours. Use short paragraphs, a compact timeline and plain sentences. No legalese.

**Required information**

- **Identifiers up front:** the order number (`GPA.…`), product, amount, purchase time (to the minute, with timezone), the Google Play account, and the Play support case ID if one exists. The payment method as shown on the receipt (for example card type and last 4 digits) helps, if the user is fine sharing it.
- **The ban:** when it happened (to the minute, with timezone) and the gap since purchase, stated plainly if it is short. Include the ban notice text **verbatim** (or its key sentences, verbatim and marked with "…" where shortened) and any reference ID it contains.
- **The developer route is exhausted:** say that the user contacted Anthropic as Google Play instructs, with dates. Quote Anthropic's refusal **verbatim** with its date and time, and say who sent it. If there were several refusals or a statement that further messages may not be answered, include that. If the Claude login differs from the Play account, explain the link in one or two sentences and say how Anthropic verified it, if they did.
- **Why Google Play should refund:** Google Play billed the user and is the merchant of record for this charge (receipt, order number, payment instrument). The developer has refused in writing, so the user has no remaining path except Google Play. The service was not delivered, because the account was banned soon after payment. Any Play cancellation notice or developer statement that supports this belongs here. Make the argument once, calmly.
- **What has already been done:** earlier Play refund requests and their outcomes, and the developer contacts. One line each.
- **The request:** ask for a review by a specialist and a refund of this order, and state the refund destination the user chose (see *Refund destination* in Step 6), with exactly the details Google needs for it. Then Google does not need another round to ask. Thank them.
- **Exhibit list:** one English sentence per exhibit (number, what it is, its timestamp). Refer to exhibits in the text as "(Exhibit 3)".
- **Sign-off** as the user prefers (their name and/or the account email). Send from the Google account that made the purchase.

Quality bar before showing the draft:

- Every number, time and quote matches the exhibits and the case sheet exactly
- Each fact appears once. No repetition, no pleading, no blame, no speculation about the ban
- Nothing in it reads like a pasted form letter
- The draft is complete enough that a specialist would not need to ask anything except where to send the money

## Step 6 - Submit through the Google Play Help Center (after approval)

Present the draft, the exhibit files and the planned channel. Wait for explicit approval. Everything below happens while signed in with the **Google account that made the purchase**.

1. **A Google Play support email thread already exists** (from `googleplay-support@google.com`, with a case ID in the subject): first ask the user for the refund destination (item 5 below), then **reply in that thread** with the message and all exhibits attached. Skip the rest of this step.
2. **Optional earlier step, self-service refund request:** https://support.google.com/googleplay/workflow/9813244, or play.google.com, then Profile, then **Payments & subscriptions**, then **Budget & order history**, then **Report a problem** on the order ([Request a refund on Google Play](https://support.google.com/googleplay/answer/15574897)). For purchases older than 48 hours this is often denied automatically with "contact the developer". That is normal and is not the case you are building.
3. **Open the case: Google Play Help, Contact Us.** Go to https://support.google.com/googleplay/gethelp (sign-in required).
   - Choose the issue about a purchase, order or subscription refund. Select the Claude order if asked.
   - Choose the reason closest to the facts, such as the item not working or not being delivered as described.
   - Choose **email** as the contact method. Chat or phone may be missing for some accounts and regions.
   - Option labels vary by region and language. Read the screen and pick the closest match. Do not guess hidden options.
   - The form may have no free-text description field. That is expected; the confirmation page may simply say that your email has been sent and show a case ID.
4. **Email 1 arrives.** Google emails from `googleplay-support@google.com` with the case ID in the subject (in English, "[<case ID>] Your Google Support Inquiry"). It is often a canned refund-policy text that says you can reply for more help.
5. **Ask the user for the refund destination now**, before sending the reply. A manual refund needs a destination, and Google asks for one if the message does not state it, which costs a round. Example of how Google asked in a real case:

   > In order to do so, we will need to know your preferred payment method:
   > - credit card - recommended, the safest and the fastest method
   > - bank account - can be used as an exception
   >
   > If you want us to refund the order to one of the credit cards added to your account, kindly get back to us once you have confirmed the last 4 digits of the correct credit card where the refund will be processed.
   >
   > In case you want the refund to be issued to your bank account, please fill out this Refund Request Form.

   Present these choices to the user (a card on the Google account, usually the one that was charged, or a bank account) and let them choose. Collect only what that choice requires: for a card, its type and last 4 digits; for a bank account, nothing in the email, since the details go into Google's own form when Google sends it. Put the choice in the message, for example "Please refund this order to the Visa card ending in NNNN on my account, which was charged for it."
6. **The real message goes in the reply.** **Reply in that thread** with the complete message from Step 5 (including the chosen refund destination) and all exhibits.
7. From then on, all communication happens in that email thread. Policy background, for your own understanding only, not for the message: [Google Play refund policies](https://support.google.com/googleplay/answer/2479637).

Do not submit the same request in several channels at once.

## Step 7 - After sending: recognize the email sequence

Tell the user what was sent, when, where, and with which attachments. Keep the case sheet up to date with each reply's date and time. Then expect this sequence:

1. **Email 1, the acknowledgement.** From `googleplay-support@google.com`, case ID in the subject. It confirms the case was received and is often canned refund-policy text that ends with an invitation to reply. It is not a decision.
2. **Email 2, the complete message.** The user's reply in that thread (Step 5 and Step 6), already stating the refund destination the user chose.
3. **Email 3, very likely a template denial.** Recognize it by phrases like these (quoted from real template denials; wording varies and may be machine-translated):
   - "we do not offer refunds in most cases and many of the refunds offered are considered one-time courtesies" (or "…considered one-time")
   - "we won’t be able to grant your refund request due to our Google Play refund policies"
   - "I was able to check the transactions and we are sorry to say that the request was denied"
   - "we highly recommend contacting the app developer for your refund request" / "we recommend that you contact the developer"
   - "the requested payments need to be investigated further through the developer"
   - "Google Play Store is just a payments platform for the app developers and acts as an intermediary"
   - "they usually reply within 3 business days" / "The developer must respond to you within three business days"
   - a pointer to the developer's support email (for Claude, `support+android@anthropic.com`) and a link to the refund policy (`support.google.com/googleplay/answer/2479637`)

   Signs it is a template: it does not mention the ban, the timeline or the developer's written refusal that the message already included, and it tells the user to do what they have already done.

**A template denial is not necessarily final.** Example: after the complete message was sent, a template denial pointing to the developer arrived, and about 6 hours later an order-cancellation receipt from `googleplay-noreply@google.com` refunded the full amount.

Suggested handling of a template denial:

1. **Consider waiting about 24 hours, then search** for an order cancellation or refund receipt from `googleplay-noreply@google.com` (for example `from:googleplay-noreply@google.com` plus the order number). A refund may arrive only as such a receipt, saying the subscription was cancelled and the payment will be refunded, with the amount, and not as a reply in the case thread. If it is there, tell the user; no reply is needed.
2. **If no receipt arrives, draft a reply** in the same thread that responds to what the template actually said. Usually that is "contact the developer first", so the reply:
   - states that the developer was already contacted (date) and refused in writing, quoting the refusal sentence with its date and pointing to the exhibit already sent ("Exhibit N");
   - asks for a specialist review and a refund of this order.
   Keep it focused on the point Google raised. There is usually no need to repeat the whole timeline or re-attach everything, but include whatever that answer needs. Still no template wording. The user approves it before it is sent. If later replies are needed, handle each the same way.

Other replies:

- If Google asks for screenshots of the developer conversation, make sure both the developer's address and the user's address are visible.
- **If Google still asks how to receive the refund** (for example because the destination changed), confirm the user's choice and answer with only the details the chosen option requires (for a card, the last 4 digits at most).
- If Google asks for time or another detail, answer briefly and only with what is asked, after the user's OK.
- After a refund is confirmed, it can take several business days to appear on the payment method.

## Bundled scripts

All scripts work from the command line and support `--help`. Coordinates are pixels or percentages (`"10%"`).

| Script | Purpose |
|---|---|
| `scripts/redact.py` | Black, fill, blur or pixelate `--rect X1,Y1,X2,Y2` / `--band Y1,Y2` (with `--band-x`) / `--ocr REGEX`. Also takes `--spec` JSON and an optional `--label`. Metadata is dropped. |
| `scripts/annotate.py` | Adds an exhibit banner (`--title`, repeatable `--caption`, `--position top\|bottom`) above or below the image without covering it, plus `--box X1,Y1,X2,Y2[:label]`, `--arrow X1,Y1,X2,Y2[:label]`, `--note X,Y:text`, `--spec` JSON, `--max-width`. |
| `scripts/grid.py` | Draws a coordinate grid on a copy of an image so you can read coordinates for the two scripts above. |

## Final privacy check

Before sending, look at every attachment one last time. Check for unrelated inbox rows, full card numbers, other people's data, tokens in URLs, and notification banners from other apps. Make sure the case sheet and exhibits are not saved inside any shared or public folder.
