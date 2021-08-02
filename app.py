from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin # for running in other country
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/', methods = ['GET'])
@cross_origin()
def homePage():
    return render_template('index.html')

############################################

@ app.route('/review', methods = ['POST', 'GET']) # route to show the review comments
@ cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString

            ## Requesting the page for Http response.
            uclient = uReq(flipkart_url)

            ## Reading the content on the page
            flipkartPage = uclient.read()
            uclient.close()

            ## Beautifying the HTML of search page ('https://www.flipkart.com/search?q=')
            flipkart_html = bs(flipkartPage, "html.parser")

            ## Find a certain information
            ## bigboxes refer to the image boxes of the products displaying in the website.
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})

            ## deleting the upper boxes will not affect the main content (why? not confirm.)
            del bigboxes[0:2]

            ## now the 0th box will be the 1st searched product.
            box = bigboxes[0]

            ## Particular product link from the inspection option - The href Statement.
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']

            ## Getting information about the particular product of which we have extracted link.
            ## testing get response
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'

            ## Beautifing prodRes - (it contains information)
            prod_html = bs(prodRes.text, "html.parser")  # extracting in textual format

            ## Getting into the reviews section of the products
            commentboxes = prod_html.findAll('div', {'class': "_16PBlm"})

            ## Saving the extracted infromation into a file
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            ####################
            reviews = []
            for commentbox in commentboxes:
                ## Name ##
                try:
                    name = commentbox.div.div.findAll('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    name = 'No Name'

                ## Ratings ##
                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    rating = 'No Rating'

                ## comment_head ##
                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    commentHead = 'No Comment Heading'

                ## comment ##
                try:
                    comtag = commentbox.div.div.findAll('div', {'class': ''})
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews) - 1)])


        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'


    else:
        return render_template('index.html')
############################################

if __name__ == '__main__':
    # app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug = True)