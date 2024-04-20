document.addEventListener('DOMContentLoaded', function() {
    fetchDataAndDrawCharts();
});

function fetchDataAndDrawCharts() {
    fetch(`/data/${hashtag}`)
        .then(response => response.json())
        .then(data => {
            drawBarChart(data);
            drawPieChart(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function drawBarChart(data) {
    try{
        const sentimentCounts = { 'Positive': 0, 'Neutral': 0, 'Negative': 0 };
        data.forEach(tweet => {
            if(tweet.Sentiment in sentimentCounts) {
                sentimentCounts[tweet.Sentiment] += 1;
            }
        });

        // Convert the counts to an array suitable for D3.js
        const sentimentData = Object.keys(sentimentCounts).map(sentiment => ({
            Sentiment: sentiment,
            Count: sentimentCounts[sentiment]
        }));

        // Visualization code here using sentimentData
        const margin = { top: 20, right: 30, bottom: 40, left: 90 },
            width = 960 - margin.left - margin.right,
            height = 400 - margin.top - margin.bottom;

        const svg = d3.select("#bar-chart").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        const x = d3.scaleBand()
            .range([0, width])
            .domain(sentimentData.map(d => d.Sentiment))
            .padding(0.1);

        const y = d3.scaleLinear()
            .domain([0, d3.max(sentimentData, d => d.Count)])
            .range([height, 0]);

        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

        svg.append("g")
            .call(d3.axisLeft(y));

        svg.selectAll("myRect")
            .data(sentimentData)
            .enter()
            .append("rect")
            .attr("x", d => x(d.Sentiment))
            .attr("y", d => y(d.Count))
            .attr("width", x.bandwidth())
            .attr("height", d => height - y(d.Count))
            .attr("fill", "#69b3a2");
       } catch (error) {
        console.error('Error in drawBarChart:', error);
        d3.select("#bar-chart").append("p").text("Failed to render bar chart due to data processing error.");
    }
}

function drawPieChart(data) {
    try {
        // Sum up the counts of each sentiment type
        const sentimentCounts = data.reduce((acc, tweet) => {
            acc[tweet.Sentiment] = (acc[tweet.Sentiment] || 0) + 1;
            return acc;
        }, {});
        const formattedData = Object.keys(sentimentCounts).map(key => ({
            label: key,
            value: sentimentCounts[key]
        }));

        var width = 300,
            height = 300,
            radius = Math.min(width, height) / 2;

        var color = d3.scaleOrdinal()
            .range(["#4daf4a", "#e41a1c", "#377eb8"]); // Adjust the color range as needed

        var svg = d3.select("#pie-chart").append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${width / 2}, ${height / 2})`);

        var arc = d3.arc()
            .innerRadius(0) // Added innerRadius for the pie chart
            .outerRadius(radius);

        var pie = d3.pie()
            .sort(null)
            .value(d => d.value);

        var g = svg.selectAll(".arc")
            .data(pie(formattedData))
            .enter().append("g")
            .attr("class", "arc");

        g.append("path")
            .attr("d", arc)
            .style("fill", d => color(d.data.label));

        g.append("text")
            .attr("transform", d => `translate(${arc.centroid(d)})`)
            .attr("dy", "0.35em")
            .attr("text-anchor", "middle")
            .text(d => d.data.label)
            .style("fill", "#fff"); // Optional: set a color for the text

    } catch (error) {
        console.error('Error in drawPieChart:', error);
        d3.select("#pie-chart").append("p").text("Failed to render pie chart due to a data processing error.");
    }
}
