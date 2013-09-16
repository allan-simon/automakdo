#! /usr/bin/env python
from httpclient import Cookie, Session
from secret import USERNAME, PASSWORD
import re

def get_csrf(text):
    for line in text.split("\n"):
        if (re.search("csrf",line)):
            return line.split("\"")[5]

session = Session(print_cookies = True)
LOGIN_URL ='/mdswo/jsp/sys/userLogin.jsp'
LOGIN_TREAT_URL ='/mdswo/jsp/sys/customerLogin.do'

ORDER_NEW_TREAT_URL = '/mdswo/jsp/order/startOrder.do'
SELECT_ITEM_TREAT_URL = '/mdswo/jsp/menu/select.do'
ADD_TO_CART_TREAT_URL = '/mdswo/jsp/menu/addToCart.do'
START_CHECKOUT_TREAT_URL = '/mdswo/jsp/order/startCheckout.do'
CONFIRM_DELIVERY_TREAT_URL = '/mdswo/jsp/order/confirmOrderDelivery.do'

NOTIFICATION_BY_EMAIL = 2
DELIVERY_IN_30_MIN = 0
# magic number get by looking at the HTML
# for other menu you "just" need to check the HTML on their website
MENU_DOUBLE_CHEESE = '1838'
# replace by the number you want ;-)
NBR_DOUBLE_CHEESE_MENU_I_WANT = 1

#if you want to add some remarks with your order (precise the address
#this kind of stuff)
REMARKS_ABOUT_THE_ORDER = ''

# we first fake we open the login page
html = session.transmit(LOGIN_URL,https = True)

#now we prepare the login post request
postData = {
    'userName' : USERNAME,
    'password' : PASSWORD,
}
loginTreatHTML = session.transmit_post_form(
    post_url = LOGIN_TREAT_URL,
    post_data_array = postData,
    https = True
)
#we are then redirected to the page to make a new order
#we get the redirected page
orderNewURL = session.get_redirection()


#now we arrive on the page to precise the address
#TODO have an option to not chose the default one
#TODO have an option to go on the "add a new address"

orderNewHTML = session.transmit(orderNewURL,https = True)
#the order new form as a csrf inside so we first get its value
#TODO check if the csrf is the same all along the session (it seems so)
csrf = get_csrf(orderNewHTML)
print(csrf)
postData = {
    'csrf' : csrf,
    #TODO magic number, the number is your address number
    # HOME_1 is 1 etc.
    'defaultAddressKey' : 1,

    'deliveryType' : DELIVERY_IN_30_MIN,
    'selectedDate' : '',
    'selectedTime' : ''
}
# we are normally redirected to the menu page
session.transmit_post_form(
    post_url = ORDER_NEW_TREAT_URL,
    post_data_array = postData,
    https = True
)

menuURL = session.get_redirection()
menuHTML = session.transmit(menuURL,https = True)
#select the one item

postData = {
    'csrf' : csrf,
    'plu' : MENU_DOUBLE_CHEESE, #magic number for double cheese
}
session.transmit_post_form(
    post_url = SELECT_ITEM_TREAT_URL,
    post_data_array = postData,
    https = True
)
selectItemURL = session.get_redirection()
selectItemHTML = session.transmit(selectItemURL,https = True)


#we arrive on the page to select precisely the item
#selectItemHTML = session.transmit(SELECT_ITEM_URL,https = True)

postData = {
    'csrf' : csrf,
    'plu' : MENU_DOUBLE_CHEESE, #magic number for double cheese
    'woItemId' : MENU_DOUBLE_CHEESE, #need to check if plu and woItemId can be different
    'selectDrink'+MENU_DOUBLE_CHEESE : 3050, #medium coke
    'selectSide'+MENU_DOUBLE_CHEESE: -1433, #it seems -1433 means 'none'
    'qtyProd'+MENU_DOUBLE_CHEESE : NBR_DOUBLE_CHEESE_MENU_I_WANT #TODO to replace
}
session.transmit_post_form(
    post_url = ADD_TO_CART_TREAT_URL,
    post_data_array = postData,
    https = True
)
selectItemURL = session.get_redirection()
selectItemHTML = session.transmit(selectItemURL,https = True)

#now we checkout
postData = {
    'csrf' : csrf
}
session.transmit_post_form(
    post_url = START_CHECKOUT_TREAT_URL,
    post_data_array = postData,
    https = True
)
orderDeliveryURL = session.get_redirection()
orderDeliveryHTML = session.transmit(orderDeliveryURL,https = True)

#we confirm everything
postData = {
    'csrf' : csrf,
    'preferredNotification' : NOTIFICATION_BY_EMAIL,
    'confirmationEmail' : USERNAME,
    'confirmationSms' : '',
    'orderRemarks' : REMARKS_ABOUT_THE_ORDER
}
session.transmit_post_form(
    post_url = CONFIRM_DELIVERY_TREAT_URL,
    post_data_array = postData,
    https = True
)
orderDeliveryURL = session.get_redirection()
orderDeliveryHTML = session.transmit(orderDeliveryURL,https = True)
