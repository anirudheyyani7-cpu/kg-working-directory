CREATE FULLTEXT INDEX entity_search IF NOT EXISTS FOR (n:Company|Technology|Standard|Product|RegBody|Market|Person|Event) ON EACH [n.name, n.description];
CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name);
CREATE INDEX technology_name IF NOT EXISTS FOR (t:Technology) ON (t.name);
CREATE INDEX standard_identifier IF NOT EXISTS FOR (s:Standard) ON (s.identifier);
CREATE INDEX standard_name IF NOT EXISTS FOR (s:Standard) ON (s.name);
CREATE INDEX regbody_name IF NOT EXISTS FOR (r:RegBody) ON (r.name);
CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name);
CREATE INDEX market_name IF NOT EXISTS FOR (m:Market) ON (m.name);
CREATE INDEX event_date IF NOT EXISTS FOR (e:Event) ON (e.date);
CREATE INDEX event_type IF NOT EXISTS FOR (e:Event) ON (e.event_type);
CREATE INDEX article_url IF NOT EXISTS FOR (a:Article) ON (a.url);
CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT technology_name_unique IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT regbody_name_unique IF NOT EXISTS FOR (r:RegBody) REQUIRE r.name IS UNIQUE;
CREATE CONSTRAINT standard_name_unique IF NOT EXISTS FOR (s:Standard) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT product_name_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT market_name_unique IF NOT EXISTS FOR (m:Market) REQUIRE m.name IS UNIQUE
