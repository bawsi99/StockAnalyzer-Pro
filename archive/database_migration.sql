-- =====================================================
-- COMPREHENSIVE DATABASE MIGRATION FOR TRADERPRO
-- Performance Optimization and Data Normalization
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================
-- 1. ENHANCED PROFILES TABLE
-- =====================================================

-- Add new columns to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(20) DEFAULT 'free';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_analysis_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS analysis_count INTEGER DEFAULT 0;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS favorite_stocks TEXT[] DEFAULT '{}';

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email) WHERE email IS NOT NULL;

-- =====================================================
-- 2. ENHANCED STOCK_ANALYSES TABLE
-- =====================================================

-- Add new columns to stock_analyses table for better querying
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS analysis_type VARCHAR(50) DEFAULT 'standard';
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS exchange VARCHAR(10) DEFAULT 'NSE';
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS period_days INTEGER;
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS interval VARCHAR(20) DEFAULT 'day';
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS overall_signal VARCHAR(20);
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS confidence_score DECIMAL(5,2);
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20);
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS current_price DECIMAL(10,2);
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS price_change_percentage DECIMAL(8,4);
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS sector VARCHAR(100);
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS analysis_quality VARCHAR(20) DEFAULT 'standard';
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS mathematical_validation BOOLEAN DEFAULT FALSE;
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS chart_paths JSONB;
ALTER TABLE stock_analyses ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stock_analyses_user_id ON stock_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_stock_analyses_stock_symbol ON stock_analyses(stock_symbol);
CREATE INDEX IF NOT EXISTS idx_stock_analyses_created_at ON stock_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_stock_analyses_overall_signal ON stock_analyses(overall_signal);
CREATE INDEX IF NOT EXISTS idx_stock_analyses_confidence_score ON stock_analyses(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_stock_analyses_sector ON stock_analyses(sector);
CREATE INDEX IF NOT EXISTS idx_stock_analyses_user_symbol ON stock_analyses(user_id, stock_symbol);
CREATE INDEX IF NOT EXISTS idx_stock_analyses_analysis_type ON stock_analyses(analysis_type);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_stock_analyses_user_created ON stock_analyses(user_id, created_at DESC);

-- =====================================================
-- 3. NEW TABLES FOR NORMALIZED DATA
-- =====================================================

-- Technical Indicators Table
CREATE TABLE IF NOT EXISTS technical_indicators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES stock_analyses(id) ON DELETE CASCADE,
    indicator_type VARCHAR(50) NOT NULL,
    indicator_name VARCHAR(100) NOT NULL,
    value DECIMAL(15,6),
    signal VARCHAR(20),
    strength DECIMAL(5,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for technical indicators
CREATE INDEX IF NOT EXISTS idx_technical_indicators_analysis_id ON technical_indicators(analysis_id);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_type ON technical_indicators(indicator_type);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_signal ON technical_indicators(signal);

-- Sector Benchmarking Table
CREATE TABLE IF NOT EXISTS sector_benchmarking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES stock_analyses(id) ON DELETE CASCADE,
    sector VARCHAR(100) NOT NULL,
    sector_index VARCHAR(50),
    beta DECIMAL(8,4),
    correlation DECIMAL(8,4),
    sharpe_ratio DECIMAL(8,4),
    volatility DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    cumulative_return DECIMAL(8,4),
    annualized_return DECIMAL(8,4),
    sector_beta DECIMAL(8,4),
    sector_correlation DECIMAL(8,4),
    sector_sharpe_ratio DECIMAL(8,4),
    sector_volatility DECIMAL(8,4),
    sector_max_drawdown DECIMAL(8,4),
    sector_cumulative_return DECIMAL(8,4),
    sector_annualized_return DECIMAL(8,4),
    excess_return DECIMAL(8,4),
    sector_excess_return DECIMAL(8,4),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for sector benchmarking
CREATE INDEX IF NOT EXISTS idx_sector_benchmarking_analysis_id ON sector_benchmarking(analysis_id);
CREATE INDEX IF NOT EXISTS idx_sector_benchmarking_sector ON sector_benchmarking(sector);
CREATE INDEX IF NOT EXISTS idx_sector_benchmarking_beta ON sector_benchmarking(beta);

-- Pattern Recognition Table
CREATE TABLE IF NOT EXISTS pattern_recognition (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES stock_analyses(id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,
    confidence DECIMAL(5,2),
    direction VARCHAR(20),
    start_date DATE,
    end_date DATE,
    start_price DECIMAL(10,2),
    end_price DECIMAL(10,2),
    target_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for pattern recognition
CREATE INDEX IF NOT EXISTS idx_pattern_recognition_analysis_id ON pattern_recognition(analysis_id);
CREATE INDEX IF NOT EXISTS idx_pattern_recognition_type ON pattern_recognition(pattern_type);
CREATE INDEX IF NOT EXISTS idx_pattern_recognition_direction ON pattern_recognition(direction);

-- Risk Management Table
CREATE TABLE IF NOT EXISTS risk_management (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES stock_analyses(id) ON DELETE CASCADE,
    risk_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_score DECIMAL(5,2),
    description TEXT,
    mitigation_strategy TEXT,
    stop_loss_level DECIMAL(10,2),
    take_profit_level DECIMAL(10,2),
    position_size_recommendation DECIMAL(5,2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for risk management
CREATE INDEX IF NOT EXISTS idx_risk_management_analysis_id ON risk_management(analysis_id);
CREATE INDEX IF NOT EXISTS idx_risk_management_type ON risk_management(risk_type);
CREATE INDEX IF NOT EXISTS idx_risk_management_level ON risk_management(risk_level);

-- Trading Levels Table
CREATE TABLE IF NOT EXISTS trading_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES stock_analyses(id) ON DELETE CASCADE,
    level_type VARCHAR(20) NOT NULL, -- 'support', 'resistance', 'entry', 'exit'
    price_level DECIMAL(10,2) NOT NULL,
    strength DECIMAL(5,2),
    volume_confirmation BOOLEAN DEFAULT FALSE,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for trading levels
CREATE INDEX IF NOT EXISTS idx_trading_levels_analysis_id ON trading_levels(analysis_id);
CREATE INDEX IF NOT EXISTS idx_trading_levels_type ON trading_levels(level_type);
CREATE INDEX IF NOT EXISTS idx_trading_levels_price ON trading_levels(price_level);

-- Multi-Timeframe Analysis Table
CREATE TABLE IF NOT EXISTS multi_timeframe_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES stock_analyses(id) ON DELETE CASCADE,
    timeframe VARCHAR(20) NOT NULL, -- 'short_term', 'medium_term', 'long_term'
    signal VARCHAR(20),
    confidence DECIMAL(5,2),
    bias VARCHAR(20),
    entry_range_min DECIMAL(10,2),
    entry_range_max DECIMAL(10,2),
    target_1 DECIMAL(10,2),
    target_2 DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for multi-timeframe analysis
CREATE INDEX IF NOT EXISTS idx_mtf_analysis_analysis_id ON multi_timeframe_analysis(analysis_id);
CREATE INDEX IF NOT EXISTS idx_mtf_analysis_timeframe ON multi_timeframe_analysis(timeframe);
CREATE INDEX IF NOT EXISTS idx_mtf_analysis_signal ON multi_timeframe_analysis(signal);

-- Volume Analysis Table
CREATE TABLE IF NOT EXISTS volume_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES stock_analyses(id) ON DELETE CASCADE,
    volume_type VARCHAR(50) NOT NULL, -- 'anomaly', 'confirmation', 'divergence'
    date DATE,
    volume DECIMAL(15,2),
    price DECIMAL(10,2),
    significance DECIMAL(5,2),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for volume analysis
CREATE INDEX IF NOT EXISTS idx_volume_analysis_analysis_id ON volume_analysis(analysis_id);
CREATE INDEX IF NOT EXISTS idx_volume_analysis_type ON volume_analysis(volume_type);
CREATE INDEX IF NOT EXISTS idx_volume_analysis_date ON volume_analysis(date);

-- =====================================================
-- 4. VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for analysis summary with key metrics
CREATE OR REPLACE VIEW analysis_summary_view AS
SELECT 
    sa.id,
    sa.stock_symbol,
    sa.user_id,
    sa.overall_signal,
    sa.confidence_score,
    sa.risk_level,
    sa.current_price,
    sa.price_change_percentage,
    sa.sector,
    sa.analysis_type,
    sa.created_at,
    p.full_name as user_name,
    p.email as user_email
FROM stock_analyses sa
LEFT JOIN profiles p ON sa.user_id = p.id
ORDER BY sa.created_at DESC;

-- View for sector performance analysis
CREATE OR REPLACE VIEW sector_performance_view AS
SELECT 
    sa.sector,
    COUNT(*) as analysis_count,
    AVG(sa.confidence_score) as avg_confidence,
    AVG(sa.price_change_percentage) as avg_price_change,
    COUNT(CASE WHEN sa.overall_signal = 'Bullish' THEN 1 END) as bullish_count,
    COUNT(CASE WHEN sa.overall_signal = 'Bearish' THEN 1 END) as bearish_count,
    COUNT(CASE WHEN sa.overall_signal = 'Neutral' THEN 1 END) as neutral_count,
    MAX(sa.created_at) as last_analysis
FROM stock_analyses sa
WHERE sa.sector IS NOT NULL
GROUP BY sa.sector
ORDER BY analysis_count DESC;

-- View for user analysis history
CREATE OR REPLACE VIEW user_analysis_history_view AS
SELECT 
    sa.user_id,
    p.full_name,
    p.email,
    COUNT(*) as total_analyses,
    COUNT(DISTINCT sa.stock_symbol) as unique_stocks,
    AVG(sa.confidence_score) as avg_confidence,
    MAX(sa.created_at) as last_analysis,
    ARRAY_AGG(DISTINCT sa.sector) FILTER (WHERE sa.sector IS NOT NULL) as sectors_analyzed
FROM stock_analyses sa
LEFT JOIN profiles p ON sa.user_id = p.id
GROUP BY sa.user_id, p.full_name, p.email
ORDER BY total_analyses DESC;

-- =====================================================
-- 5. FUNCTIONS FOR DATA MIGRATION AND UTILITIES
-- =====================================================

-- Function to extract and store technical indicators from JSON
CREATE OR REPLACE FUNCTION extract_technical_indicators(analysis_id UUID)
RETURNS VOID AS $$
DECLARE
    analysis_data JSONB;
    indicators JSONB;
    indicator_type TEXT;
    indicator_name TEXT;
    indicator_value JSONB;
BEGIN
    -- Get analysis data
    SELECT analysis_data INTO analysis_data 
    FROM stock_analyses 
    WHERE id = analysis_id;
    
    IF analysis_data IS NULL THEN
        RETURN;
    END IF;
    
    -- Extract indicators from the JSON structure
    indicators = analysis_data->'indicators';
    
    IF indicators IS NULL THEN
        RETURN;
    END IF;
    
    -- Clear existing indicators for this analysis
    DELETE FROM technical_indicators WHERE analysis_id = extract_technical_indicators.analysis_id;
    
    -- Extract moving averages
    IF indicators ? 'moving_averages' THEN
        FOR indicator_name, indicator_value IN SELECT * FROM jsonb_each(indicators->'moving_averages')
        LOOP
            INSERT INTO technical_indicators (analysis_id, indicator_type, indicator_name, value, signal, strength)
            VALUES (
                analysis_id,
                'moving_average',
                indicator_name,
                (indicator_value->>'value')::DECIMAL,
                indicator_value->>'signal',
                (indicator_value->>'strength')::DECIMAL
            );
        END LOOP;
    END IF;
    
    -- Extract RSI
    IF indicators ? 'rsi' THEN
        INSERT INTO technical_indicators (analysis_id, indicator_type, indicator_name, value, signal, strength)
        VALUES (
            analysis_id,
            'momentum',
            'RSI',
            (indicators->'rsi'->>'value')::DECIMAL,
            indicators->'rsi'->>'signal',
            (indicators->'rsi'->>'strength')::DECIMAL
        );
    END IF;
    
    -- Extract MACD
    IF indicators ? 'macd' THEN
        INSERT INTO technical_indicators (analysis_id, indicator_type, indicator_name, value, signal, strength)
        VALUES (
            analysis_id,
            'momentum',
            'MACD',
            (indicators->'macd'->>'value')::DECIMAL,
            indicators->'macd'->>'signal',
            (indicators->'macd'->>'strength')::DECIMAL
        );
    END IF;
    
    -- Extract Bollinger Bands
    IF indicators ? 'bollinger_bands' THEN
        INSERT INTO technical_indicators (analysis_id, indicator_type, indicator_name, value, signal, strength)
        VALUES (
            analysis_id,
            'volatility',
            'Bollinger_Bands',
            (indicators->'bollinger_bands'->>'value')::DECIMAL,
            indicators->'bollinger_bands'->>'signal',
            (indicators->'bollinger_bands'->>'strength')::DECIMAL
        );
    END IF;
    
END;
$$ LANGUAGE plpgsql;

-- Function to extract and store sector benchmarking data
CREATE OR REPLACE FUNCTION extract_sector_benchmarking(analysis_id UUID)
RETURNS VOID AS $$
DECLARE
    analysis_data JSONB;
    sector_data JSONB;
BEGIN
    -- Get analysis data
    SELECT analysis_data INTO analysis_data 
    FROM stock_analyses 
    WHERE id = analysis_id;
    
    IF analysis_data IS NULL THEN
        RETURN;
    END IF;
    
    -- Extract sector benchmarking
    sector_data = analysis_data->'sector_benchmarking';
    
    IF sector_data IS NULL THEN
        RETURN;
    END IF;
    
    -- Clear existing sector data for this analysis
    DELETE FROM sector_benchmarking WHERE analysis_id = extract_sector_benchmarking.analysis_id;
    
    -- Insert sector benchmarking data
    INSERT INTO sector_benchmarking (
        analysis_id,
        sector,
        sector_index,
        beta,
        correlation,
        sharpe_ratio,
        volatility,
        max_drawdown,
        cumulative_return,
        annualized_return,
        sector_beta,
        sector_correlation,
        sector_sharpe_ratio,
        sector_volatility,
        sector_max_drawdown,
        sector_cumulative_return,
        sector_annualized_return,
        excess_return,
        sector_excess_return
    ) VALUES (
        analysis_id,
        sector_data->'sector_info'->>'sector',
        sector_data->'sector_info'->>'sector_index',
        (sector_data->'market_benchmarking'->>'beta')::DECIMAL,
        (sector_data->'market_benchmarking'->>'correlation')::DECIMAL,
        (sector_data->'market_benchmarking'->>'sharpe_ratio')::DECIMAL,
        (sector_data->'market_benchmarking'->>'volatility')::DECIMAL,
        (sector_data->'market_benchmarking'->>'max_drawdown')::DECIMAL,
        (sector_data->'market_benchmarking'->>'cumulative_return')::DECIMAL,
        (sector_data->'market_benchmarking'->>'annualized_return')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_beta')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_correlation')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_sharpe_ratio')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_volatility')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_max_drawdown')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_cumulative_return')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_annualized_return')::DECIMAL,
        (sector_data->'market_benchmarking'->>'excess_return')::DECIMAL,
        (sector_data->'sector_benchmarking'->>'sector_excess_return')::DECIMAL
    );
    
END;
$$ LANGUAGE plpgsql;

-- Function to extract and store pattern recognition data
CREATE OR REPLACE FUNCTION extract_pattern_recognition(analysis_id UUID)
RETURNS VOID AS $$
DECLARE
    analysis_data JSONB;
    overlays JSONB;
    patterns JSONB;
    pattern JSONB;
BEGIN
    -- Get analysis data
    SELECT analysis_data INTO analysis_data 
    FROM stock_analyses 
    WHERE id = analysis_id;
    
    IF analysis_data IS NULL THEN
        RETURN;
    END IF;
    
    -- Extract overlays (contains patterns)
    overlays = analysis_data->'overlays';
    
    IF overlays IS NULL THEN
        RETURN;
    END IF;
    
    -- Clear existing patterns for this analysis
    DELETE FROM pattern_recognition WHERE analysis_id = extract_pattern_recognition.analysis_id;
    
    -- Extract triangle patterns
    IF overlays ? 'triangle_patterns' THEN
        FOR pattern IN SELECT * FROM jsonb_array_elements(overlays->'triangle_patterns')
        LOOP
            INSERT INTO pattern_recognition (
                analysis_id, pattern_type, pattern_name, confidence, direction,
                start_date, end_date, start_price, end_price, target_price, stop_loss
            ) VALUES (
                analysis_id,
                'triangle',
                pattern->>'type',
                (pattern->>'confidence')::DECIMAL,
                pattern->>'direction',
                (pattern->>'start_date')::DATE,
                (pattern->>'end_date')::DATE,
                (pattern->>'start_price')::DECIMAL,
                (pattern->>'end_price')::DECIMAL,
                (pattern->>'target_price')::DECIMAL,
                (pattern->>'stop_loss')::DECIMAL
            );
        END LOOP;
    END IF;
    
    -- Extract flag patterns
    IF overlays ? 'flag_patterns' THEN
        FOR pattern IN SELECT * FROM jsonb_array_elements(overlays->'flag_patterns')
        LOOP
            INSERT INTO pattern_recognition (
                analysis_id, pattern_type, pattern_name, confidence, direction,
                start_date, end_date, start_price, end_price, target_price, stop_loss
            ) VALUES (
                analysis_id,
                'flag',
                pattern->>'type',
                (pattern->>'confidence')::DECIMAL,
                pattern->>'direction',
                (pattern->>'start_date')::DATE,
                (pattern->>'end_date')::DATE,
                (pattern->>'start_price')::DECIMAL,
                (pattern->>'end_price')::DECIMAL,
                (pattern->>'target_price')::DECIMAL,
                (pattern->>'stop_loss')::DECIMAL
            );
        END LOOP;
    END IF;
    
END;
$$ LANGUAGE plpgsql;

-- Function to extract and store trading levels
CREATE OR REPLACE FUNCTION extract_trading_levels(analysis_id UUID)
RETURNS VOID AS $$
DECLARE
    analysis_data JSONB;
    ai_analysis JSONB;
    trading_guidance JSONB;
    levels JSONB;
    level JSONB;
BEGIN
    -- Get analysis data
    SELECT analysis_data INTO analysis_data 
    FROM stock_analyses 
    WHERE id = analysis_id;
    
    IF analysis_data IS NULL THEN
        RETURN;
    END IF;
    
    -- Extract AI analysis
    ai_analysis = analysis_data->'ai_analysis';
    
    IF ai_analysis IS NULL THEN
        RETURN;
    END IF;
    
    -- Clear existing trading levels for this analysis
    DELETE FROM trading_levels WHERE analysis_id = extract_trading_levels.analysis_id;
    
    -- Extract key levels from AI analysis
    IF ai_analysis ? 'must_watch_levels' THEN
        FOR level IN SELECT * FROM jsonb_array_elements(ai_analysis->'must_watch_levels')
        LOOP
            INSERT INTO trading_levels (
                analysis_id, level_type, price_level, strength, description
            ) VALUES (
                analysis_id,
                'key_level',
                (level->>'price')::DECIMAL,
                (level->>'strength')::DECIMAL,
                level->>'description'
            );
        END LOOP;
    END IF;
    
    -- Extract trading guidance levels
    trading_guidance = ai_analysis->'trading_strategy';
    
    IF trading_guidance IS NOT NULL THEN
        -- Short term levels
        IF trading_guidance ? 'short_term' THEN
            INSERT INTO trading_levels (analysis_id, level_type, price_level, strength, description)
            VALUES (
                analysis_id,
                'entry',
                (trading_guidance->'short_term'->>'entry_range'->0)::DECIMAL,
                0.8,
                'Short term entry level'
            );
            
            INSERT INTO trading_levels (analysis_id, level_type, price_level, strength, description)
            VALUES (
                analysis_id,
                'target',
                (trading_guidance->'short_term'->>'targets'->0)::DECIMAL,
                0.9,
                'Short term target 1'
            );
            
            INSERT INTO trading_levels (analysis_id, level_type, price_level, strength, description)
            VALUES (
                analysis_id,
                'stop_loss',
                (trading_guidance->'short_term'->>'stop_loss')::DECIMAL,
                0.9,
                'Short term stop loss'
            );
        END IF;
    END IF;
    
END;
$$ LANGUAGE plpgsql;

-- Function to extract and store volume analysis
CREATE OR REPLACE FUNCTION extract_volume_analysis(analysis_id UUID)
RETURNS VOID AS $$
DECLARE
    analysis_data JSONB;
    overlays JSONB;
    volume_anomalies JSONB;
    anomaly JSONB;
BEGIN
    -- Get analysis data
    SELECT analysis_data INTO analysis_data 
    FROM stock_analyses 
    WHERE id = analysis_id;
    
    IF analysis_data IS NULL THEN
        RETURN;
    END IF;
    
    -- Extract overlays
    overlays = analysis_data->'overlays';
    
    IF overlays IS NULL THEN
        RETURN;
    END IF;
    
    -- Clear existing volume analysis for this analysis
    DELETE FROM volume_analysis WHERE analysis_id = extract_volume_analysis.analysis_id;
    
    -- Extract volume anomalies
    IF overlays ? 'volume_anomalies' THEN
        FOR anomaly IN SELECT * FROM jsonb_array_elements(overlays->'volume_anomalies')
        LOOP
            INSERT INTO volume_analysis (
                analysis_id, volume_type, date, volume, price, significance, description
            ) VALUES (
                analysis_id,
                'anomaly',
                (anomaly->>'date')::DATE,
                (anomaly->>'volume')::DECIMAL,
                (anomaly->>'price')::DECIMAL,
                0.8,
                'Volume anomaly detected'
            );
        END LOOP;
    END IF;
    
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. TRIGGERS FOR AUTOMATIC DATA EXTRACTION
-- =====================================================

-- Trigger function to automatically extract data when analysis is inserted/updated
CREATE OR REPLACE FUNCTION trigger_extract_analysis_data()
RETURNS TRIGGER AS $$
BEGIN
    -- Extract all data types
    PERFORM extract_technical_indicators(NEW.id);
    PERFORM extract_sector_benchmarking(NEW.id);
    PERFORM extract_pattern_recognition(NEW.id);
    PERFORM extract_trading_levels(NEW.id);
    PERFORM extract_volume_analysis(NEW.id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS extract_analysis_data_trigger ON stock_analyses;
CREATE TRIGGER extract_analysis_data_trigger
    AFTER INSERT OR UPDATE ON stock_analyses
    FOR EACH ROW
    EXECUTE FUNCTION trigger_extract_analysis_data();

-- =====================================================
-- 7. PERFORMANCE OPTIMIZATION
-- =====================================================

-- Enable parallel query execution
ALTER TABLE stock_analyses SET (parallel_workers = 4);
ALTER TABLE technical_indicators SET (parallel_workers = 4);
ALTER TABLE sector_benchmarking SET (parallel_workers = 4);
ALTER TABLE pattern_recognition SET (parallel_workers = 4);

-- Set appropriate fill factor for tables that are frequently updated
ALTER TABLE stock_analyses SET (fillfactor = 90);
ALTER TABLE technical_indicators SET (fillfactor = 90);

-- =====================================================
-- 8. DATA MIGRATION COMMANDS
-- =====================================================

-- Update existing records with extracted data
-- This will be run after the migration to populate the new tables
-- UPDATE stock_analyses SET analysis_data = analysis_data WHERE id IS NOT NULL;

-- =====================================================
-- 9. CLEANUP AND MAINTENANCE
-- =====================================================

-- Create a function to clean up old analysis data
CREATE OR REPLACE FUNCTION cleanup_old_analyses(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM stock_analyses 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get analysis statistics
CREATE OR REPLACE FUNCTION get_analysis_statistics()
RETURNS TABLE (
    total_analyses BIGINT,
    total_users BIGINT,
    avg_confidence DECIMAL,
    most_analyzed_sector TEXT,
    most_analyzed_stock TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_analyses,
        COUNT(DISTINCT user_id) as total_users,
        AVG(confidence_score) as avg_confidence,
        (SELECT sector FROM sector_performance_view ORDER BY analysis_count DESC LIMIT 1) as most_analyzed_sector,
        (SELECT stock_symbol FROM stock_analyses GROUP BY stock_symbol ORDER BY COUNT(*) DESC LIMIT 1) as most_analyzed_stock
    FROM stock_analyses;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Create a comment documenting the migration
COMMENT ON DATABASE postgres IS 'TraderPro Database - Optimized for high-performance stock analysis with normalized data structure'; 