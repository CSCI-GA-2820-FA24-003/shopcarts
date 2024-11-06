Feature: The shopcarts service back-end
    As a Shopcarts eCommerce Manager
    I need a RESTful catalog service
    So that I can keep track of all my customer's shopcarts.

    Background:
        Given the following shopcarts
            | customer_name |
            | Alice         |
            | Bob           |
        And the following items
            | customer_name | name  | description  | price | quantity | is_urgent |
            | Alice         | hat   | hat clothing | 2.45  | 12       | False     |
            | Bob           | shirt | hat clothing | 20.23 | 23       | False     |

    Scenario: Background test