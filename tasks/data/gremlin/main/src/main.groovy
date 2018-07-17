import com.tinkerpop.gremlin.groovy.
graph = JanusGraphFactory.open('conf/janusgraph-berkeleyje-es.properties')
mgmt = graph.openManagement()