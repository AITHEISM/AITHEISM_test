# Get all points for a specific round
@app.get("/discussion/rounds/{round_num}/points")
async def get_round_points(
    round_num: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取特定轮次的所有观点"""
    try:
        logger.info(f"Getting points for round: {round_num}")
        
        round_data = read_round_data(round_num)
        if not round_data or "points" not in round_data:
            raise HTTPException(
                status_code=404,
                detail=f"Round {round_num} not found or has no points"
            )
        
        points = round_data["points"]
        total_points = len(points)
        
        # 计算分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_points = points[start_idx:end_idx]
        
        # 处理每个观点的响应和时间戳
        formatted_points = []
        for point in paginated_points:
            point_id = point.get("id")
            if not point_id:
                timestamp = point.get("timestamp")
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.isoformat()
                elif not isinstance(timestamp, str):
                    timestamp = datetime.utcnow().isoformat()
                point_id = f"point_{datetime.fromisoformat(timestamp).strftime('%Y%m%d_%H%M%S')}"
            
            formatted_points.append({
                "id": point_id,
                "content": point["content"],
                "timestamp": point.get("timestamp"),
                "agreements": len(point.get("agreements", [])),
                "disagreements": len(point.get("disagreements", [])),
                "responses": point.get("agreements", []) + point.get("disagreements", [])
            })
        
        return {
            "points": formatted_points,
            "pagination": {
                "total": total_points,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_points + page_size - 1) // page_size,
                "has_more": end_idx < total_points
            },
            "roundNum": round_num
        }
        
    except Exception as e:
        logger.error(f"Error getting round points: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
