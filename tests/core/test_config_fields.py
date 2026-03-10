from semantic_scholar_skills.config import AuthorDetailFields, CitationReferenceFields


def test_author_detail_fields_include_current_nested_paper_allowlist() -> None:
    expected = {
        "papers.citationCount",
        "papers.citationStyles",
        "papers.corpusId",
        "papers.externalIds",
        "papers.fieldsOfStudy",
        "papers.influentialCitationCount",
        "papers.isOpenAccess",
        "papers.journal",
        "papers.openAccessPdf",
        "papers.paperId",
        "papers.publicationDate",
        "papers.publicationTypes",
        "papers.publicationVenue",
        "papers.referenceCount",
        "papers.s2FieldsOfStudy",
        "papers.title",
    }

    assert expected.issubset(AuthorDetailFields.VALID_FIELDS)


def test_citation_reference_fields_include_current_spec_fields() -> None:
    expected = {
        "citationStyles",
        "contextsWithIntent",
        "corpusId",
        "externalIds",
        "fieldsOfStudy",
        "isOpenAccess",
        "journal",
        "openAccessPdf",
        "publicationDate",
        "publicationTypes",
        "publicationVenue",
        "referenceCount",
        "s2FieldsOfStudy",
    }

    assert expected.issubset(CitationReferenceFields.VALID_FIELDS)
