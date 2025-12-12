export interface AtomicContext {
    id: string;
    folder_name: string;
    timestamp: string;
    batch_id: string;
    created_at: string;
}

export interface AtomicArtifact {
    id: string;
    context_id: string;
    filename: string;
    file_type: string;
    file_hash: string;
    local_path: string;
    content?: string;
}

export interface ArtifactEmbedding {
    id: string;
    artifact_id: string;
    embedding: number[];
    metadata: any;
}
