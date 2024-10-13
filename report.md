# Report

## The Test
In my tests, I ran the code for 5 minutes with clients sending randomized messages at varying intervals. I conducted 3 attempts each for 1, 2, 5, 10, 20, 50, 100, and 200 clients to evaluate performance and message handling.

### General Trend;
As the number of clients increases, the server performs well, managing a steady flow of messages from up to 100 clients. The messages sent and received are fairly consistent, showing that the server can handle a significant amount of traffic without much trouble.
However, when the number of clients reaches 100, there's a noticeable drop in the server's ability to process messages. While the number of messages sent by the clients remains the same, the server is only able to receive a small amount of them. This suggests that the code is unable to record the correct number being sent by the clients due to the increase in the number of I/Os and the obvious print messages being expensive to execute. There is also an anomaly recorded at 50 clients where the value became extremely large. This should be ignored/ommitted in understanding the complete trend

### Error Trends:
Errors such as 'Broken pipe' and 'Connection reset by peer' become extremely frequent as the number of clients increases, especially beyond 50 clients. These errors typically occur due to clients disconnecting abruptly or network instability under heavy load.

### Conclusion
The server performs well in handling messages and managing client connections with up to 50 clients, with minimal issues. However, as the number of clients increases to 100 and 200, performance noticeably declines, with fewer messages being received compared to those sent. This suggests the server encounters bottlenecks due to the increased I/O operations and the cost of managing numerous connections simultaneously. The server however demonstrates to be sturdy in performance as it receives messages and handles failures in a graceful way