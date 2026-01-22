-- =========================
-- STRUCTURE ACADEMIQUE
-- =========================

CREATE TABLE departements (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE formations (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    dept_id INT REFERENCES departements(id),
    niveau VARCHAR(10),
    nb_modules INT
);

CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(150),
    credits INT,
    formation_id INT REFERENCES formations(id)
);

-- =========================
-- USERS (AUTHENTICATION)
-- =========================

CREATE TYPE user_role AS ENUM ('admin', 'dean', 'dept_head', 'professor', 'student');

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    professeur_id INT REFERENCES professeurs(id),
    etudiant_id INT REFERENCES etudiants(id)
);

CREATE INDEX idx_users_username ON users(username);

-- =========================
-- ACTEURS
-- =========================

CREATE TABLE etudiants (
    id SERIAL PRIMARY KEY,
    matricule VARCHAR(20) UNIQUE,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    formation_id INT REFERENCES formations(id),
    promo INT
);

CREATE TABLE professeurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100),
    dept_id INT REFERENCES departements(id),
    specialite VARCHAR(100)
);

-- =========================
-- INSCRIPTIONS
-- =========================

CREATE TABLE inscriptions (
    etudiant_id INT REFERENCES etudiants(id),
    module_id INT REFERENCES modules(id),
    PRIMARY KEY (etudiant_id, module_id)
);

-- =========================
-- INFRASTRUCTURE
-- =========================

CREATE TABLE batiments (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100)
);

CREATE TABLE salles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50),
    capacite INT,
    type VARCHAR(20),
    batiment_id INT REFERENCES batiments(id)
);

-- =========================
-- EXAMENS
-- =========================

CREATE TABLE examens (
    id SERIAL PRIMARY KEY,
    module_id INT REFERENCES modules(id),
    date DATE,
    heure TIME,
    duree INT,
    dept_head_approved INT DEFAULT 0,
    vice_dean_approved INT DEFAULT 0
);

CREATE TABLE examens_salles (
    examen_id INT REFERENCES examens(id),
    salle_id INT REFERENCES salles(id),
    PRIMARY KEY (examen_id, salle_id)
);

CREATE TABLE surveillances (
    examen_id INT REFERENCES examens(id),
    prof_id INT REFERENCES professeurs(id),
    PRIMARY KEY (examen_id, prof_id)
);

CREATE INDEX idx_inscriptions_etudiant ON inscriptions(etudiant_id);
CREATE INDEX idx_inscriptions_module ON inscriptions(module_id);
CREATE INDEX idx_examens_date ON examens(date);
CREATE INDEX idx_surveillances_prof ON surveillances(prof_id);
CREATE INDEX idx_salles_capacite ON salles(capacite);

-- =========================
-- QUERY 1 : TRIGGER
-- Limiter les surveillances des professeurs à 3 par jour
-- =========================
CREATE OR REPLACE FUNCTION check_prof_surveillance()
RETURNS TRIGGER AS $$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM surveillances s
        JOIN examens e ON s.examen_id = e.id
        WHERE s.prof_id = NEW.prof_id
          AND e.date = (SELECT date FROM examens WHERE id = NEW.examen_id)
    ) >= 3 THEN
        RAISE EXCEPTION 'Le professeur dépasse le maximum de 3 surveillances par jour';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_prof_surveillance
BEFORE INSERT ON surveillances
FOR EACH ROW
EXECUTE FUNCTION check_prof_surveillance();

-- =========================
-- QUERY 2 : INSERT DEPARTEMENTS
-- Ajouter les départements
-- =========================
INSERT INTO departements (nom) VALUES ('Informatique'), ('Mathématiques');

-- =========================
-- QUERY 3 : INSERT FORMATIONS
-- Ajouter les formations
-- =========================
INSERT INTO formations (nom, dept_id, niveau, nb_modules) VALUES 
('Licence Info', 1, 'L1', 6),
('Licence Math', 2, 'L1', 6);

-- =========================
-- QUERY 4 : INSERT MODULES
-- Ajouter les modules
-- =========================
INSERT INTO modules (nom, credits, formation_id) VALUES
('Algo', 5, 1),
('BD', 5, 1),
('Analyse', 5, 2);

-- =========================
-- QUERY 5 : INSERT ETUDIANTS
-- Ajouter les étudiants
-- =========================
INSERT INTO etudiants (matricule, nom, prenom, formation_id, promo) VALUES
('E001', 'Dupont', 'Alice', 1, 2025),
('E002', 'Martin', 'Bob', 1, 2025),
('E003', 'Durand', 'Claire', 2, 2025);

-- =========================
-- QUERY 6 : INSERT PROFESSEURS
-- Ajouter les professeurs
-- =========================
INSERT INTO professeurs (nom, dept_id, specialite) VALUES
('Durand', 1, 'Algo'),
('Petit', 2, 'Analyse');

-- =========================
-- QUERY 7 : INSERT BATIMENTS
-- Ajouter les bâtiments
-- =========================
INSERT INTO batiments (nom) VALUES ('Bâtiment A'), ('Bâtiment B');

-- =========================
-- QUERY 8 : INSERT SALLES
-- Ajouter les salles
-- =========================
INSERT INTO salles (nom, capacite, type, batiment_id) VALUES
('Amphi 1', 100, 'amphi', 1),
('Salle 101', 20, 'salle', 1);

-- =========================
-- QUERY 9 : INSERT EXAMENS
-- Ajouter les examens
-- =========================
INSERT INTO examens (module_id, date, heure, duree) VALUES
(1, '2026-01-15', '09:00', 120),
(2, '2026-01-15', '14:00', 90),
(3, '2026-01-16', '09:00', 120);

-- =========================
-- QUERY 10 : INSERT EXAMENS_SALLES
-- Associer examens et salles
-- =========================
INSERT INTO examens_salles (examen_id, salle_id) VALUES
(1, 1),
(2, 2),
(3, 1);

-- =========================
-- QUERY 11 : INSERT INSCRIPTIONS
-- Ajouter des inscriptions pour tester conflits étudiants et capacité salles
-- =========================
INSERT INTO inscriptions (etudiant_id, module_id) VALUES
(1, 1),
(1, 2),  -- conflit : 2 examens le même jour pour étudiant 1
(2, 1),
(3, 3);

-- =========================
-- QUERY 12 : INSERT SURVEILLANCES
-- Ajouter les surveillances des professeurs
-- =========================
INSERT INTO surveillances (examen_id, prof_id) VALUES
(1, 1),
(2, 1),
(3, 2);

-- =========================
-- QUERY 13 : CONFLITS ETUDIANTS
-- Vérifier si un étudiant a plus d’un examen le même jour
-- =========================
SELECT e.id AS etudiant,
       ex.date,
       COUNT(*) AS nb_examens
FROM etudiants e
JOIN inscriptions i ON e.id = i.etudiant_id
JOIN examens ex ON i.module_id = ex.module_id
GROUP BY e.id, ex.date
HAVING COUNT(*) > 1;

-- =========================
-- QUERY 14 : CAPACITE SALLES
-- Vérifier si le nombre d’inscrits dépasse la capacité totale des salles pour un examen
-- =========================
SELECT ex.id AS examen,
       COUNT(i.etudiant_id) AS inscrits,
       SUM(s.capacite) AS capacite_totale
FROM examens ex
JOIN examens_salles es ON ex.id = es.examen_id
JOIN salles s ON es.salle_id = s.id
JOIN inscriptions i ON i.module_id = ex.module_id
GROUP BY ex.id
HAVING COUNT(i.etudiant_id) > SUM(s.capacite);

INSERT INTO surveillances (examen_id, prof_id) VALUES (3, 1);

-- =========================
-- QUERY 15 : ADD MORE EXAMPLE DATA FOR TIMETABLE GENERATOR TESTING
-- =========================

-- Add more departments
INSERT INTO departements (nom) VALUES 
('Physique'), 
('Chimie'), 
('Biologie'),
('Économie')
ON CONFLICT (nom) DO NOTHING;

-- Add more formations
INSERT INTO formations (nom, dept_id, niveau, nb_modules) VALUES 
('Licence Info', 1, 'L2', 6),
('Licence Info', 1, 'L3', 6),
('Master Info', 1, 'M1', 5),
('Master Info', 1, 'M2', 5),
('Licence Math', 2, 'L2', 6),
('Licence Math', 2, 'L3', 6),
('Licence Physique', 3, 'L1', 6),
('Licence Chimie', 4, 'L1', 6)
ON CONFLICT DO NOTHING;

-- Add more modules
INSERT INTO modules (nom, credits, formation_id) VALUES
-- L2 Info
('Réseaux', 5, 2),
('Systèmes d''exploitation', 5, 2),
('Programmation Web', 5, 2),
('Bases de données avancées', 5, 2),
('Intelligence Artificielle', 5, 2),
('Sécurité informatique', 5, 2),
-- L3 Info
('Architecture logicielle', 5, 3),
('Cloud Computing', 5, 3),
('Big Data', 5, 3),
('Machine Learning', 5, 3),
('Projet de fin d''études', 10, 3),
('Stage', 10, 3),
-- M1 Info
('Deep Learning', 6, 4),
('DevOps', 6, 4),
('Blockchain', 6, 4),
('Cybersécurité', 6, 4),
('Gestion de projet', 6, 4),
-- M2 Info
('Mémoire', 15, 5),
('Stage professionnel', 15, 5),
-- L2 Math
('Algèbre linéaire', 5, 6),
('Analyse numérique', 5, 6),
('Probabilités', 5, 6),
('Statistiques', 5, 6),
('Topologie', 5, 6),
('Géométrie', 5, 6),
-- L3 Math
('Équations différentielles', 5, 7),
('Analyse fonctionnelle', 5, 7),
('Théorie des groupes', 5, 7),
('Calcul stochastique', 5, 7),
('Mémoire', 10, 7),
('Stage', 10, 7),
-- L1 Physique
('Mécanique', 5, 8),
('Électromagnétisme', 5, 8),
('Thermodynamique', 5, 8),
('Optique', 5, 8),
('Physique quantique', 5, 8),
('Physique expérimentale', 5, 8),
-- L1 Chimie
('Chimie organique', 5, 9),
('Chimie inorganique', 5, 9),
('Chimie analytique', 5, 9),
('Biochimie', 5, 9),
('Chimie physique', 5, 9),
('Travaux pratiques', 5, 9);

-- Add more students (50 students)
INSERT INTO etudiants (matricule, nom, prenom, formation_id, promo) VALUES
('E004', 'Bernard', 'David', 1, 2025),
('E005', 'Moreau', 'Emma', 1, 2025),
('E006', 'Lefebvre', 'Lucas', 1, 2025),
('E007', 'Simon', 'Sophie', 1, 2025),
('E008', 'Laurent', 'Thomas', 1, 2025),
('E009', 'Petit', 'Marie', 2, 2025),
('E010', 'Garcia', 'Pierre', 2, 2025),
('E011', 'Roux', 'Julie', 2, 2025),
('E012', 'Fournier', 'Antoine', 2, 2025),
('E013', 'Girard', 'Camille', 2, 2025),
('E014', 'Bonnet', 'Léa', 3, 2025),
('E015', 'Dupuis', 'Nicolas', 3, 2025),
('E016', 'Lambert', 'Sarah', 3, 2025),
('E017', 'Fontaine', 'Alexandre', 3, 2025),
('E018', 'Rousseau', 'Manon', 3, 2025),
('E019', 'Vincent', 'Hugo', 4, 2025),
('E020', 'Muller', 'Inès', 4, 2025),
('E021', 'Lefevre', 'Maxime', 4, 2025),
('E022', 'Boyer', 'Chloé', 4, 2025),
('E023', 'Garnier', 'Romain', 4, 2025),
('E024', 'Faure', 'Élise', 5, 2025),
('E025', 'Blanc', 'Paul', 5, 2025),
('E026', 'Guerin', 'Laura', 5, 2025),
('E027', 'Masson', 'Julien', 5, 2025),
('E028', 'Jean', 'Anaïs', 5, 2025),
('E029', 'Noel', 'Baptiste', 6, 2025),
('E030', 'Henry', 'Émilie', 6, 2025),
('E031', 'Roussel', 'Quentin', 6, 2025),
('E032', 'Mathieu', 'Léna', 6, 2025),
('E033', 'Gautier', 'Adrien', 6, 2025),
('E034', 'Dumont', 'Océane', 7, 2025),
('E035', 'Francois', 'Matthieu', 7, 2025),
('E036', 'Mercier', 'Justine', 7, 2025),
('E037', 'Dufour', 'Benjamin', 7, 2025),
('E038', 'Bertrand', 'Amélie', 7, 2025),
('E039', 'Roux', 'Florian', 8, 2025),
('E040', 'Lucas', 'Margot', 8, 2025),
('E041', 'Brun', 'Cédric', 8, 2025),
('E042', 'Blanchard', 'Marion', 8, 2025),
('E043', 'Giraud', 'Sébastien', 8, 2025),
('E044', 'Joly', 'Lucie', 9, 2025),
('E045', 'Colin', 'Guillaume', 9, 2025),
('E046', 'Arnaud', 'Pauline', 9, 2025),
('E047', 'Fabre', 'Vincent', 9, 2025),
('E048', 'Aubert', 'Clara', 9, 2025),
('E049', 'Roche', 'Yann', 1, 2024),
('E050', 'Clement', 'Éva', 2, 2024),
('E051', 'Marchand', 'Rémi', 3, 2024),
('E052', 'Lopez', 'Charlotte', 4, 2024),
('E053', 'Dupont', 'Louis', 5, 2024);

-- Add more professors (15 professors)
INSERT INTO professeurs (nom, dept_id, specialite) VALUES
('Martin', 1, 'Réseaux'),
('Bernard', 1, 'Systèmes'),
('Dubois', 1, 'Web'),
('Moreau', 1, 'IA'),
('Laurent', 1, 'Sécurité'),
('Simon', 2, 'Algèbre'),
('Michel', 2, 'Analyse'),
('Garcia', 2, 'Probabilités'),
('David', 2, 'Statistiques'),
('Bertrand', 3, 'Mécanique'),
('Roux', 3, 'Électromagnétisme'),
('Vincent', 4, 'Chimie organique'),
('Fournier', 4, 'Biochimie'),
('Girard', 1, 'Cloud'),
('Lefebvre', 1, 'Big Data');

-- Add more buildings and rooms
INSERT INTO batiments (nom) VALUES 
('Bâtiment C'), 
('Bâtiment D'),
('Bâtiment E')
ON CONFLICT DO NOTHING;

INSERT INTO salles (nom, capacite, type, batiment_id) VALUES
-- Bâtiment A
('Amphi 2', 150, 'amphi', 1),
('Salle 102', 20, 'salle', 1),
('Salle 103', 20, 'salle', 1),
('Salle 104', 20, 'salle', 1),
('Salle 105', 20, 'salle', 1),
-- Bâtiment B
('Amphi 3', 120, 'amphi', 2),
('Salle 201', 20, 'salle', 2),
('Salle 202', 20, 'salle', 2),
('Salle 203', 20, 'salle', 2),
('Salle 204', 20, 'salle', 2),
('Salle 205', 20, 'salle', 2),
-- Bâtiment C
('Amphi 4', 100, 'amphi', 3),
('Salle 301', 20, 'salle', 3),
('Salle 302', 20, 'salle', 3),
('Salle 303', 20, 'salle', 3),
('Salle 304', 20, 'salle', 3),
-- Bâtiment D
('Amphi 5', 80, 'amphi', 4),
('Salle 401', 20, 'salle', 4),
('Salle 402', 20, 'salle', 4),
('Salle 403', 20, 'salle', 4),
-- Bâtiment E
('Amphi 6', 90, 'amphi', 5),
('Salle 501', 20, 'salle', 5),
('Salle 502', 20, 'salle', 5);

-- Add student enrollments (inscriptions) - enroll students in multiple modules
INSERT INTO inscriptions (etudiant_id, module_id) 
SELECT e.id, m.id
FROM etudiants e
CROSS JOIN modules m
WHERE e.formation_id = m.formation_id
ON CONFLICT DO NOTHING;

-- =========================
-- QUERY 16 : USERS WILL BE CREATED VIA seed_users.py SCRIPT
-- Run: python backend/seed_users.py after database setup
-- Password for all users: "password123"
-- =========================
