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
            | customer_name | name  | description   | price | quantity | is_urgent |
            | Alice         | hat   | hat clothing  | 2.45  | 12       | False     |
            | Alice         | pant  | pant clothing | 8.75  | 2        | True      |
            | Bob           | shirt | hat clothing  | 20.23 | 23       | False     |

    Scenario: The server is running
        When I visit the "Management Page"
        Then I should see "Shopcarts Service Management" in the header
        And I should not see "404 Not Found"

    Scenario: List all shopcarts
        When I visit the "Management Page"
        And I press the "List" button
        Then I should see the message "Success"
        And I should see "hat" in the results
        And I should see "pant" in the results
        And I should not see "bicycle" in the results

    Scenario: Create a shopcart
        When I visit the "Management Page"
        And I set the "Customer Name" to "Eve"
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        And the "Customer Name" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "Eve" in the "Customer Name" field
