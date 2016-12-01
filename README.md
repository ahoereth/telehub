# GitHub Webhooks Telegram Bot

I can send you or a group you add me to notifications about activity
on specified GitHub repos. I will notify you about new commits,
issues and comments. [Contact me on telegram](https://telegram.me/TelehubRobot)

1. Go to your repositorie's `settings`
2. Select `Webhooks` and then the `add webhook` button in the top right
  * *Payload URL*: `https://telegit.vega.uberspace.de/`
  * *Content type*: `application/json`
  * *Secret*: Something secret -- we will need it later!
  * *Events*: For information on which events I can handle, type `/events`.
  * *Activity*: Checked!
3. [Send me a message](https://telegram.me/TelehubRobot) with `/subscribe <username>/<repo> <secret>`
