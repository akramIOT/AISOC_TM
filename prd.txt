# product-backlog
Purpose: All new features, bugs, customer requests will be curated in this repo. We will use the issues created here to flesh out features, designs, and requirements. 

*What happens here, doesn't stay here*
- The issues reported in this repo will be worked on in other Hypothesis repos. 
- Issues created in #product-backlog will serve as parent cards that track all information about that request. 
- All Google docs, PR info, or issues created in other repos must be linked back to issues created in this repo. 
- We're implementing this system so that we can have complete transparency around our product developement process.

# Backlog Requirements - Product Specific 

1. "Create a query to alert when any API endpoint experiences a 50% increase in average response time compared to the previous hour's baseline."

2. "Users have reported unusual account activity. Create monitoring to detect anomalous user session patterns that could indicate account compromise. Consider factors like login frequency, concurrent sessions, and access patterns."

3. "Monitor for scenarios where error rates exceed 5% of total requests per endpoint while also having high response times (>2s) in the last 15 minutes."

4. "The application seems slow during peak hours. Create a query to help us understand what's causing it."

5. "Create proactive monitoring for resource utilization across our microservices. We need early warning when any service is trending towards capacity limits, considering historical usage patterns and growth rates."
