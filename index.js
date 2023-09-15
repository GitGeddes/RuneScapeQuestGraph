// import * as d3 from './node_modules/d3/dist/d3.js';
// import * as d3Force from './node_modules/d3-force/dist/d3-force.js';

// https://observablehq.com/@d3/disjoint-force-directed-graph/2

const LINK_STRENGTH = 0.5;
const LINK_DISTANCE = 30;
const CHARGE_STRENGTH = -50;
const CENTER_STRENGTH = 0.1;
const GRAVITY_STRENGTH = 0.07;
const BOUNDS_PADDING = 0.05;

const LINK_WIDTH_NORMAL = 1;
const HOVER_LINK_INCREASE = 5;
const HOVER_LINK_DECREASE = 0.5

const NODE_RADIUS_NORMAL = 5;
const HOVER_NODE_RADIUS_INCREASE = 10;
const HOVER_NODE_RADIUS_DECREASE = 4;

var nodes = [];
var links = [];

d3.json('./quests.json').then((data) => {
    // Load and parse data from JSON file
    for (var key in data) {
        parseNode(data[key]);
    }
    // Select SVG element in DOM.
    // Requires local HTTP server to load local files. Opening index.html as a file doesn't work.
    const svg = d3.select("svg"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    // Zoom
    function handleZoom(e) {
        svg.attr('transform', e.transform);
    }
    svg.call(d3.zoom()
        .extent([[0, 0], [width, height]])
        .scaleExtent([1, 8])
        .on("zoom", handleZoom));

    // Call-able color method to generate a color for a given string.
    const color = d3.scaleOrdinal(d3.schemeCategory10);

    // Build force simulation with given parameters.
    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.name).strength(LINK_STRENGTH).distance(LINK_DISTANCE))
        .force("charge", d3.forceManyBody().strength(CHARGE_STRENGTH))
        .force("center", d3.forceCenter(width / 2, height / 2).strength(CENTER_STRENGTH))
        .force("forceX", d3.forceX(width / 2).strength(GRAVITY_STRENGTH))
        .force("forceY", d3.forceY(height / 2). strength(GRAVITY_STRENGTH));

    // Add links to the SVG.
    const link = svg.append("g")
        .attr("stroke", "#999")
        .attr("stroke-opacity", 0.6)
        .selectAll("line")
        .data(links)
        .enter().append("line")
            .attr("stroke-width", 1);

    // Add nodes to the SVG.
    const node = svg.append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .selectAll("circle")
        .data(nodes)
        .enter().append("circle")
            .attr("r", NODE_RADIUS_NORMAL)
            .attr("fill", d => color(d.name));

    // Show node name on hover.
    node.append("title")
        .text(d => d.name);
    node.append("text")
        .style("position", "absolute")
        .style("visibility", "visible")
        .text(d => d.name);

    // Change styling on hover.
    node.on("mouseover", d => {
        const name = d.target.__data__.name;
        const neighbors = getNeighbors(name);
        d3.selectAll("circle")
            // .filter(c => c.name === d.target.__data__.name)
            .transition()
            .duration(1)
            .attr("r", n => {
                if (name === n.name || neighbors.includes(n.name)) return HOVER_NODE_RADIUS_INCREASE;
                else return HOVER_NODE_RADIUS_DECREASE;
            });
        d3.selectAll("circle")
            .filter(c => c.name === d.target.__data__.name)
            .append("text")
            .attr("class", "tooltip")
        link.style("stroke-width", l => {
            const name = d.target.__data__.name;
            if (name === l.source.name || name === l.target.name) return HOVER_LINK_INCREASE;
            else return HOVER_LINK_DECREASE;
        });
    }).on("mouseout", (d) => {
        d3.selectAll("circle")
            // .filter(c => c.name === d.target.__data__.name)
            .transition()
            .duration(1)
            .attr("r", NODE_RADIUS_NORMAL);
        link.style("stroke-width", LINK_WIDTH_NORMAL);
    });

    // Add a drag behavior.
    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Set the position attributes of links and nodes each time the simulation ticks.
    simulation.on("tick", () => tick(link, node));

    // Reheat the simulation when drag starts, and fix the subject position.
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }

    // Update the subject (dragged node) position during drag.
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }

    // Restore the target alpha so the simulation cools after dragging ends.
    // Unfix the subject position now that it’s no longer being dragged.
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }

    function checkBounds(d) {
        if (d.x < width * BOUNDS_PADDING) d.x = width * BOUNDS_PADDING;
        if (d.x > width * (1 - BOUNDS_PADDING)) d.x = width * (1 - BOUNDS_PADDING);
        if (d.y < height * BOUNDS_PADDING) d.y = height * BOUNDS_PADDING;
        if (d.y > height * (1 - BOUNDS_PADDING)) d.y = height * (1 - BOUNDS_PADDING);
    }

    function tick(link, node) {
        // link.attr("x1", d => d.source.x)
        //     .attr("y1", d => d.source.y)
        //     .attr("x2", d => d.target.x)
        //     .attr("y2", d => d.target.y);

        // node.attr("cx", d => d.x)
        //     .attr("cy", d => d.y);

        link.attr("x1", d => { 
            checkBounds(d.source);
            return d.source.x;
        })
        .attr("y1", d => d.source.y)
        .attr("x2", d => { 
            checkBounds(d.target);
            return d.target.x;
        })
        .attr("y2", d => d.target.y);

        node.attr("transform", d => {
            checkBounds(d);
            return "translate(" + d.x + ", " + d.y + ")";
        });
    }

    function getNeighbors(name) {
        var neighbors = [];
        links.forEach(link => {
            if (link.source.name === name) {
                neighbors.push(link.target.name);
            } else if (link.target.name === name) {
                neighbors.push(link.source.name);
            }
        });
        return neighbors;
    }
});

function parseNode(obj) {
    nodes.push({ "name": obj.name });
    obj.reqs.forEach(req => {
        links.push({ "source": obj.name, "target": req.name });
    })
}
