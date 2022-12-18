## Inspiration
Lots of  people around me buy stocks. However, stock prices change really fast especially during pandemic, and I know some of my friends who haven't used any stock platform would like to try without paying any money. Therefore, I would like to build a stock trading simulator which users can simulate trading stocks.

## What it does
This is a web based stock trading simulator, which users can buy and sell stocks.
![This is an image](/1.png)

![This is an image](/2.png)

## How we built it
Tech stacks and tools using Python, Flask, PostgreSQL, sqlalchemy, Jinja2. 
API used Twelve Data.


## Challenges we ran into
The hardest part is to get real-time stock data plotted in UI. We followed the instruction on Twelve Data pypi document, but hard to find a way to get the images transferred from the chart. After looked up couple pages of how other people solved the issue, we used fig.write_image after we got the chart from plotly tool, and then saved the images to the file. In the HTML page, we sourced the path.

The second challenge is we had the data to get all real-time price, but due to the price for upgrate, we decided changed to hard code right now.

## Accomplishments that we're proud of
Really proud of ourselves that finished this project ahead of time and learned new stuffs such as creating chart.

## What we learned
Team collab, communications, development structure and more!

## What's next for Stock Trading Simulator
We would like to add more feature such as search function and with more stock data. Also, we would like to combine crypo info as well.