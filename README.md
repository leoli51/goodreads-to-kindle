# goodreads-to-kindle
Send books in your GoodReads' "Want to read" to your eReader

## Run with python

 ### 1. Install requirements
```sh
pip install -r requirements.txt
```

 ### 2. Create `.env` file (or rename `template.env` to `.env`)

```properties
EMAIL_SMTP=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=example@gmail.com  # add your email
EMAIL_PASSWORD=your_password  # add your email app password
KINDLE_EMAIL=example@kindle.com  # add your kindle email
GOODREADS_ID=012345678-your-id  # add your goodreads id
RAPID_API_HOST=your_rapid_api_host  # add your rapid api host
RAPID_API_KEY=your_rapid_api_key  # add your rapid api key
ROBOTSTXT_OBEY=True  # Crawl responsibly by adhering to robots.txt rules!
```
If you use Gmail, `EMAIL_PASSWORD` must be generated following [this guide](https://support.google.com/mail/answer/185833).

`GOODREADS_ID` is the last part of the URL of your Goodreads' account.

`RAPID_API_HOST` and `RAPID_API_KEY` should be set to use an API service that allows you to download only books that you can obtain legally, without infringing any copyright. So, please do not use APIs [like this](https://rapidapi.com/tribestick-tribestick-default/api/annas-archive-api) or similar.

Also, be sure to never change `ROBOTSTXT_OBEY` in order to comply with [`robots.txt`](https://www.goodreads.com/robots.txt) rules, no matter if you want to access your own data.

If you use a Kindle eReader, you can find your `KINDLE_EMAIL` [here](https://www.amazon.com/sendtokindle/email). The link also explains how to set `EMAIL_FROM` as a recognized source for your Kindle. I have no idea if other companies' eReaders support something similar.

### 3. Run

```sh
cd goodreads_to_kindle
python main.py
```

## Run with `docker compose`

After having configured your `.env` file, run
```sh
docker-compose up -d
```
to build the container and run it in the background.
