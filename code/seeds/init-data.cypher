// 🚀 NerdMatch Database Initialization
// This script initializes the database with 20 test profiles

// Create indexes
CREATE INDEX ON :User(id);
CREATE INDEX ON :User(email);
CREATE INDEX ON :Profile(nickname);
CREATE INDEX ON :InterestCategory(name);
CREATE INDEX ON :Technology(name);

// System interests
CREATE (i1:InterestCategory {name: "Programování", type: "SYSTEM"});
CREATE (i2:InterestCategory {name: "Sci-Fi", type: "SYSTEM"});
CREATE (i3:InterestCategory {name: "Videohry", type: "SYSTEM"});
CREATE (i4:InterestCategory {name: "Fantasy", type: "SYSTEM"});
CREATE (i5:InterestCategory {name: "Komiksové knihy", type: "SYSTEM"});
CREATE (i6:InterestCategory {name: "Matematika", type: "SYSTEM"});
CREATE (i7:InterestCategory {name: "Fyzika", type: "SYSTEM"});
CREATE (i8:InterestCategory {name: "Umělá inteligence", type: "SYSTEM"});
CREATE (i9:InterestCategory {name: "Robotika", type: "SYSTEM"});
CREATE (i10:InterestCategory {name: "Anime", type: "SYSTEM"});

// System technologies
CREATE (t1:Technology {name: "Python", category: "Languages"});
CREATE (t2:Technology {name: "JavaScript", category: "Languages"});
CREATE (t3:Technology {name: "Java", category: "Languages"});
CREATE (t4:Technology {name: "C++", category: "Languages"});
CREATE (t5:Technology {name: "Go", category: "Languages"});
CREATE (t6:Technology {name: "Rust", category: "Languages"});
CREATE (t7:Technology {name: "React", category: "Frameworks"});
CREATE (t8:Technology {name: "Flask", category: "Frameworks"});
CREATE (t9:Technology {name: "Node.js", category: "Frameworks"});
CREATE (t10:Technology {name: "Docker", category: "DevOps"});
CREATE (t11:Technology {name: "Kubernetes", category: "DevOps"});
CREATE (t12:Technology {name: "MongoDB", category: "Databases"});
CREATE (t13:Technology {name: "PostgreSQL", category: "Databases"});
CREATE (t14:Technology {name: "Neo4j", category: "Databases"});
CREATE (t15:Technology {name: "Git", category: "Tools"});
CREATE (t16:Technology {name: "AWS", category: "Cloud"});
CREATE (t17:Technology {name: "Azure", category: "Cloud"});
CREATE (t18:Technology {name: "GCP", category: "Cloud"});
CREATE (t19:Technology {name: "GraphQL", category: "APIs"});
CREATE (t20:Technology {name: "REST", category: "APIs"});

// Test Users and Profiles
CREATE (u1:User {id: "alice", email: "alice@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a1:Account {is_deleted: false, last_login: datetime()})
CREATE (p1:Profile {nickname: "Alice", bio: "Programátor, která miluje sci-fi a AI", nerd_level: 8, created_at: datetime()})
CREATE (u1)-[:HAS_ACCOUNT]->(a1)
CREATE (u1)-[:HAS_PROFILE]->(p1)
CREATE (p1)-[:INTERESTED_IN]->(i1)
CREATE (p1)-[:INTERESTED_IN]->(i2)
CREATE (p1)-[:INTERESTED_IN]->(i8)
CREATE (p1)-[:LIKES_TECHNOLOGY]->(t1)
CREATE (p1)-[:LIKES_TECHNOLOGY]->(t7)
CREATE (p1)-[:LIKES_TECHNOLOGY]->(t10);

CREATE (u2:User {id: "bob", email: "bob@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a2:Account {is_deleted: false, last_login: datetime()})
CREATE (p2:Profile {nickname: "Bob", bio: "Gamer & JavaScript vývojář", nerd_level: 7, created_at: datetime()})
CREATE (u2)-[:HAS_ACCOUNT]->(a2)
CREATE (u2)-[:HAS_PROFILE]->(p2)
CREATE (p2)-[:INTERESTED_IN]->(i3)
CREATE (p2)-[:INTERESTED_IN]->(i1)
CREATE (p2)-[:INTERESTED_IN]->(i4)
CREATE (p2)-[:LIKES_TECHNOLOGY]->(t2)
CREATE (p2)-[:LIKES_TECHNOLOGY]->(t9)
CREATE (p2)-[:LIKES_TECHNOLOGY]->(t15);

CREATE (u3:User {id: "charlie", email: "charlie@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a3:Account {is_deleted: false, last_login: datetime()})
CREATE (p3:Profile {nickname: "Charlie", bio: "DevOps inženýr, milovník cloud technologií", nerd_level: 9, created_at: datetime()})
CREATE (u3)-[:HAS_ACCOUNT]->(a3)
CREATE (u3)-[:HAS_PROFILE]->(p3)
CREATE (p3)-[:INTERESTED_IN]->(i1)
CREATE (p3)-[:INTERESTED_IN]->(i7)
CREATE (p3)-[:INTERESTED_IN]->(i9)
CREATE (p3)-[:LIKES_TECHNOLOGY]->(t5)
CREATE (p3)-[:LIKES_TECHNOLOGY]->(t10)
CREATE (p3)-[:LIKES_TECHNOLOGY]->(t11);

CREATE (u4:User {id: "diana", email: "diana@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a4:Account {is_deleted: false, last_login: datetime()})
CREATE (p4:Profile {nickname: "Diana", bio: "Matematik a puzzle milovnice", nerd_level: 6, created_at: datetime()})
CREATE (u4)-[:HAS_ACCOUNT]->(a4)
CREATE (u4)-[:HAS_PROFILE]->(p4)
CREATE (p4)-[:INTERESTED_IN]->(i6)
CREATE (p4)-[:INTERESTED_IN]->(i1)
CREATE (p4)-[:INTERESTED_IN]->(i5)
CREATE (p4)-[:LIKES_TECHNOLOGY]->(t1)
CREATE (p4)-[:LIKES_TECHNOLOGY]->(t13);

CREATE (u5:User {id: "evan", email: "evan@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a5:Account {is_deleted: false, last_login: datetime()})
CREATE (p5:Profile {nickname: "Evan", bio: "Sci-fi nerd, čte sci-fi a hraje RPG hry", nerd_level: 8, created_at: datetime()})
CREATE (u5)-[:HAS_ACCOUNT]->(a5)
CREATE (u5)-[:HAS_PROFILE]->(p5)
CREATE (p5)-[:INTERESTED_IN]->(i2)
CREATE (p5)-[:INTERESTED_IN]->(i3)
CREATE (p5)-[:INTERESTED_IN]->(i4)
CREATE (p5)-[:LIKES_TECHNOLOGY]->(t3)
CREATE (p5)-[:LIKES_TECHNOLOGY]->(t4);

CREATE (u6:User {id: "fiona", email: "fiona@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a6:Account {is_deleted: false, last_login: datetime()})
CREATE (p6:Profile {nickname: "Fiona", bio: "Rust vývojářka s vášní pro bezpečnost", nerd_level: 9, created_at: datetime()})
CREATE (u6)-[:HAS_ACCOUNT]->(a6)
CREATE (u6)-[:HAS_PROFILE]->(p6)
CREATE (p6)-[:INTERESTED_IN]->(i1)
CREATE (p6)-[:INTERESTED_IN]->(i9)
CREATE (p6)-[:INTERESTED_IN]->(i7)
CREATE (p6)-[:LIKES_TECHNOLOGY]->(t6)
CREATE (p6)-[:LIKES_TECHNOLOGY]->(t19);

CREATE (u7:User {id: "george", email: "george@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a7:Account {is_deleted: false, last_login: datetime()})
CREATE (p7:Profile {nickname: "George", bio: "Frontend vývojář, React specialista", nerd_level: 7, created_at: datetime()})
CREATE (u7)-[:HAS_ACCOUNT]->(a7)
CREATE (u7)-[:HAS_PROFILE]->(p7)
CREATE (p7)-[:INTERESTED_IN]->(i1)
CREATE (p7)-[:INTERESTED_IN]->(i3)
CREATE (p7)-[:INTERESTED_IN]->(i5)
CREATE (p7)-[:LIKES_TECHNOLOGY]->(t2)
CREATE (p7)-[:LIKES_TECHNOLOGY]->(t7)
CREATE (p7)-[:LIKES_TECHNOLOGY]->(t15);

CREATE (u8:User {id: "hannah", email: "hannah@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a8:Account {is_deleted: false, last_login: datetime()})
CREATE (p8:Profile {nickname: "Hannah", bio: "Data scientist a machine learning nadšenka", nerd_level: 8, created_at: datetime()})
CREATE (u8)-[:HAS_ACCOUNT]->(a8)
CREATE (u8)-[:HAS_PROFILE]->(p8)
CREATE (p8)-[:INTERESTED_IN]->(i1)
CREATE (p8)-[:INTERESTED_IN]->(i8)
CREATE (p8)-[:INTERESTED_IN]->(i6)
CREATE (p8)-[:LIKES_TECHNOLOGY]->(t1)
CREATE (p8)-[:LIKES_TECHNOLOGY]->(t12);

CREATE (u9:User {id: "ivan", email: "ivan@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a9:Account {is_deleted: false, last_login: datetime()})
CREATE (p9:Profile {nickname: "Ivan", bio: "Anime fanoušek, milovník Asian kultury", nerd_level: 7, created_at: datetime()})
CREATE (u9)-[:HAS_ACCOUNT]->(a9)
CREATE (u9)-[:HAS_PROFILE]->(p9)
CREATE (p9)-[:INTERESTED_IN]->(i10)
CREATE (p9)-[:INTERESTED_IN]->(i3)
CREATE (p9)-[:INTERESTED_IN]->(i4)
CREATE (p9)-[:LIKES_TECHNOLOGY]->(t2)
CREATE (p9)-[:LIKES_TECHNOLOGY]->(t9);

CREATE (u10:User {id: "julia", email: "julia@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a10:Account {is_deleted: false, last_login: datetime()})
CREATE (p10:Profile {nickname: "Julia", bio: "Fullstack vývojářka, Python & JavaScript", nerd_level: 8, created_at: datetime()})
CREATE (u10)-[:HAS_ACCOUNT]->(a10)
CREATE (u10)-[:HAS_PROFILE]->(p10)
CREATE (p10)-[:INTERESTED_IN]->(i1)
CREATE (p10)-[:INTERESTED_IN]->(i2)
CREATE (p10)-[:INTERESTED_IN]->(i8)
CREATE (p10)-[:LIKES_TECHNOLOGY]->(t1)
CREATE (p10)-[:LIKES_TECHNOLOGY]->(t2)
CREATE (p10)-[:LIKES_TECHNOLOGY]->(t8);

CREATE (u11:User {id: "kevin", email: "kevin@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a11:Account {is_deleted: false, last_login: datetime()})
CREATE (p11:Profile {nickname: "Kevin", bio: "DevSecOps specialista", nerd_level: 9, created_at: datetime()})
CREATE (u11)-[:HAS_ACCOUNT]->(a11)
CREATE (u11)-[:HAS_PROFILE]->(p11)
CREATE (p11)-[:INTERESTED_IN]->(i1)
CREATE (p11)-[:INTERESTED_IN]->(i9)
CREATE (p11)-[:INTERESTED_IN]->(i7)
CREATE (p11)-[:LIKES_TECHNOLOGY]->(t6)
CREATE (p11)-[:LIKES_TECHNOLOGY]->(t11)
CREATE (p11)-[:LIKES_TECHNOLOGY]->(t16);

CREATE (u12:User {id: "lisa", email: "lisa@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a12:Account {is_deleted: false, last_login: datetime()})
CREATE (p12:Profile {nickname: "Lisa", bio: "Game developer, Unity & Unreal", nerd_level: 8, created_at: datetime()})
CREATE (u12)-[:HAS_ACCOUNT]->(a12)
CREATE (u12)-[:HAS_PROFILE]->(p12)
CREATE (p12)-[:INTERESTED_IN]->(i3)
CREATE (p12)-[:INTERESTED_IN]->(i1)
CREATE (p12)-[:INTERESTED_IN]->(i9)
CREATE (p12)-[:LIKES_TECHNOLOGY]->(t4)
CREATE (p12)-[:LIKES_TECHNOLOGY]->(t5);

CREATE (u13:User {id: "mark", email: "mark@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a13:Account {is_deleted: false, last_login: datetime()})
CREATE (p13:Profile {nickname: "Mark", bio: "Database architect, SQL guru", nerd_level: 7, created_at: datetime()})
CREATE (u13)-[:HAS_ACCOUNT]->(a13)
CREATE (u13)-[:HAS_PROFILE]->(p13)
CREATE (p13)-[:INTERESTED_IN]->(i1)
CREATE (p13)-[:INTERESTED_IN]->(i7)
CREATE (p13)-[:INTERESTED_IN]->(i6)
CREATE (p13)-[:LIKES_TECHNOLOGY]->(t12)
CREATE (p13)-[:LIKES_TECHNOLOGY]->(t13)
CREATE (p13)-[:LIKES_TECHNOLOGY]->(t14);

CREATE (u14:User {id: "nina", email: "nina@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a14:Account {is_deleted: false, last_login: datetime()})
CREATE (p14:Profile {nickname: "Nina", bio: "Fyzička a vědecky orientovaná", nerd_level: 9, created_at: datetime()})
CREATE (u14)-[:HAS_ACCOUNT]->(a14)
CREATE (u14)-[:HAS_PROFILE]->(p14)
CREATE (p14)-[:INTERESTED_IN]->(i7)
CREATE (p14)-[:INTERESTED_IN]->(i1)
CREATE (p14)-[:INTERESTED_IN]->(i6)
CREATE (p14)-[:LIKES_TECHNOLOGY]->(t1)
CREATE (p14)-[:LIKES_TECHNOLOGY]->(t2);

CREATE (u15:User {id: "oscar", email: "oscar@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a15:Account {is_deleted: false, last_login: datetime()})
CREATE (p15:Profile {nickname: "Oscar", bio: "Cloud architect, AWS certified", nerd_level: 8, created_at: datetime()})
CREATE (u15)-[:HAS_ACCOUNT]->(a15)
CREATE (u15)-[:HAS_PROFILE]->(p15)
CREATE (p15)-[:INTERESTED_IN]->(i1)
CREATE (p15)-[:INTERESTED_IN]->(i9)
CREATE (p15)-[:INTERESTED_IN]->(i8)
CREATE (p15)-[:LIKES_TECHNOLOGY]->(t16)
CREATE (p15)-[:LIKES_TECHNOLOGY]->(t17)
CREATE (p15)-[:LIKES_TECHNOLOGY]->(t11);

CREATE (u16:User {id: "patricia", email: "patricia@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a16:Account {is_deleted: false, last_login: datetime()})
CREATE (p16:Profile {nickname: "Patricia", bio: "Comicbook geek, Marvel fan", nerd_level: 6, created_at: datetime()})
CREATE (u16)-[:HAS_ACCOUNT]->(a16)
CREATE (u16)-[:HAS_PROFILE]->(p16)
CREATE (p16)-[:INTERESTED_IN]->(i5)
CREATE (p16)-[:INTERESTED_IN]->(i2)
CREATE (p16)-[:INTERESTED_IN]->(i4)
CREATE (p16)-[:LIKES_TECHNOLOGY]->(t2);

CREATE (u17:User {id: "quinn", email: "quinn@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a17:Account {is_deleted: false, last_login: datetime()})
CREATE (p17:Profile {nickname: "Quinn", bio: "Blockchain developer, crypto enthusiast", nerd_level: 8, created_at: datetime()})
CREATE (u17)-[:HAS_ACCOUNT]->(a17)
CREATE (u17)-[:HAS_PROFILE]->(p17)
CREATE (p17)-[:INTERESTED_IN]->(i1)
CREATE (p17)-[:INTERESTED_IN]->(i8)
CREATE (p17)-[:INTERESTED_IN]->(i9)
CREATE (p17)-[:LIKES_TECHNOLOGY]->(t1)
CREATE (p17)-[:LIKES_TECHNOLOGY]->(t5);

CREATE (u18:User {id: "rachel", email: "rachel@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a18:Account {is_deleted: false, last_login: datetime()})
CREATE (p18:Profile {nickname: "Rachel", bio: "Mobile developer, iOS & Android", nerd_level: 7, created_at: datetime()})
CREATE (u18)-[:HAS_ACCOUNT]->(a18)
CREATE (u18)-[:HAS_PROFILE]->(p18)
CREATE (p18)-[:INTERESTED_IN]->(i1)
CREATE (p18)-[:INTERESTED_IN]->(i3)
CREATE (p18)-[:INTERESTED_IN]->(i2)
CREATE (p18)-[:LIKES_TECHNOLOGY]->(t2)
CREATE (p18)-[:LIKES_TECHNOLOGY]->(t7)
CREATE (p18)-[:LIKES_TECHNOLOGY]->(t9);

CREATE (u19:User {id: "stefan", email: "stefan@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a19:Account {is_deleted: false, last_login: datetime()})
CREATE (p19:Profile {nickname: "Stefan", bio: "API designer, REST & GraphQL guru", nerd_level: 8, created_at: datetime()})
CREATE (u19)-[:HAS_ACCOUNT]->(a19)
CREATE (u19)-[:HAS_PROFILE]->(p19)
CREATE (p19)-[:INTERESTED_IN]->(i1)
CREATE (p19)-[:INTERESTED_IN]->(i8)
CREATE (p19)-[:INTERESTED_IN]->(i6)
CREATE (p19)-[:LIKES_TECHNOLOGY]->(t19)
CREATE (p19)-[:LIKES_TECHNOLOGY]->(t20)
CREATE (p19)-[:LIKES_TECHNOLOGY]->(t9);

CREATE (u20:User {id: "tara", email: "tara@example.com", password_hash: "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUm", created_at: datetime()})
CREATE (a20:Account {is_deleted: false, last_login: datetime()})
CREATE (p20:Profile {nickname: "Tara", bio: "QA tester, automation specialist", nerd_level: 7, created_at: datetime()})
CREATE (u20)-[:HAS_ACCOUNT]->(a20)
CREATE (u20)-[:HAS_PROFILE]->(p20)
CREATE (p20)-[:INTERESTED_IN]->(i1)
CREATE (p20)-[:INTERESTED_IN]->(i9)
CREATE (p20)-[:INTERESTED_IN]->(i6)
CREATE (p20)-[:LIKES_TECHNOLOGY]->(t1)
CREATE (p20)-[:LIKES_TECHNOLOGY]->(t15);
