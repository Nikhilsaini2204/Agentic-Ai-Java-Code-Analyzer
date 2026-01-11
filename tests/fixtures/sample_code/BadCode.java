package com.example;

import java.sql.*;

/**
 * Sample code with multiple issues for testing the agent.
 * The agent should identify security, complexity, and style issues.
 */
public class BadCode {

    // Hardcoded credentials (SECURITY ISSUE)
    private static final String DB_PASSWORD = "admin123";

    /**
     * Processes user data - has SQL injection vulnerability
     */
    public void processUserData(String userId) {
        // TODO: Add input validation

        try {
            Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost/db",
                "root",
                DB_PASSWORD
            );

            // SQL INJECTION VULNERABILITY!
            String query = "SELECT * FROM users WHERE id = '" + userId + "'";
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery(query);

            while (rs.next()) {
                // Using System.out instead of logger (STYLE ISSUE)
                System.out.println("User: " + rs.getString("name"));
                System.out.println("Email: " + rs.getString("email"));
            }

            rs.close();
            stmt.close();
            conn.close();

        } catch (Exception e) {
            // Bad error handling (BUG)
            e.printStackTrace();
        }
    }

    /**
     * Calculates discount - overly complex and has magic numbers
     */
    public int calculateDiscount(int orderTotal, int customerType) {
        int discount = 0;

        // HIGH COMPLEXITY - deeply nested if statements
        if (customerType == 1) {
            if (orderTotal > 1000) {
                if (orderTotal > 5000) {
                    if (orderTotal > 10000) {
                        if (orderTotal > 20000) {
                            discount = 30;  // Magic number
                        } else {
                            discount = 25;  // Magic number
                        }
                    } else {
                        discount = 20;  // Magic number
                    }
                } else {
                    discount = 15;  // Magic number
                }
            } else {
                discount = 10;  // Magic number
            }
        } else if (customerType == 2) {
            if (orderTotal > 1000) {
                if (orderTotal > 5000) {
                    discount = 35;  // Magic number
                } else {
                    discount = 25;  // Magic number
                }
            } else {
                discount = 20;  // Magic number
            }
        } else if (customerType == 3) {
            discount = 40;  // Magic number
        }

        return discount;
    }

    /**
     * Logs a message - should use proper logging framework
     */
    public void logMessage(String message) {
        // STYLE ISSUE - should use logger
        System.out.println("[LOG] " + message);
    }

    /**
     * Empty catch block example
     */
    public void riskyOperation() {
        try {
            // Some risky code
            int result = 100 / 0;
        } catch (Exception e) {
            // Empty catch block - swallows exceptions (BUG)
        }
    }
}